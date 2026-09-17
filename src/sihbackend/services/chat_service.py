from typing import List, Tuple
import os
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.schemas.chat import ChatResponse, EvidenceItem
from sihbackend.services.reranker import rerank_documents

# Load environment variables from .env
load_dotenv()

# Explicitly define which LLM provider to use. 
# Set this in your .env file: ACTIVE_LLM="openai"
# 
# Available values:
# "google"  - Uses Gemini 3.6 Flash (Requires GEMINI_API_KEY)
# "openai"  - Uses gpt-4o-mini (Requires OPENAI_API_KEY)
# "groq"    - Uses Llama-3.1-70b via Groq (Requires GROQ_API_KEY)
# "mistral" - Uses Mistral Large (Requires MISTRAL_API_KEY)
ACTIVE_LLM = os.environ.get("ACTIVE_LLM", "google").lower()

LLM_PROVIDER = None

if ACTIVE_LLM == "google":
    google_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if google_key:
        LLM_PROVIDER = "google"
        from langchain_google_genai import ChatGoogleGenerativeAI
    else:
        logging.error("ACTIVE_LLM is set to 'google' but no GEMINI_API_KEY is found.")
elif ACTIVE_LLM == "openai":
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        LLM_PROVIDER = "openai"
        from langchain_openai import ChatOpenAI
    else:
        logging.error("ACTIVE_LLM is set to 'openai' but no OPENAI_API_KEY is found.")
elif ACTIVE_LLM == "groq":
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        LLM_PROVIDER = "groq"
        from langchain_groq import ChatGroq
    else:
        logging.error("ACTIVE_LLM is set to 'groq' but no GROQ_API_KEY is found.")
elif ACTIVE_LLM == "mistral":
    mistral_key = os.environ.get("MISTRAL_API_KEY")
    if mistral_key:
        LLM_PROVIDER = "mistral"
        from langchain_mistralai import ChatMistralAI
    else:
        logging.error("ACTIVE_LLM is set to 'mistral' but no MISTRAL_API_KEY is found.")
else:
    logging.warning(f"Unknown ACTIVE_LLM value: {ACTIVE_LLM}. Valid options are 'google', 'openai', 'groq', or 'mistral'.")

_embeddings = None
_vectorstore_prior_art = None
_vectorstore_legal = None

def _get_vectorstores():
    global _embeddings, _vectorstore_prior_art, _vectorstore_legal
    if _embeddings is None:
        _embeddings = get_embeddings_model()
    
    if _vectorstore_prior_art is None:
        _vectorstore_prior_art = Chroma(
            persist_directory="vectorstore/prior_art",
            embedding_function=_embeddings
        )
        
    if _vectorstore_legal is None:
        try:
            _vectorstore_legal = Chroma(
                persist_directory="vectorstore/legal",
                embedding_function=_embeddings
            )
        except Exception:
            _vectorstore_legal = None
        
    return _vectorstore_prior_art, _vectorstore_legal

class RAGAnalysisOutput(BaseModel):
    executive_answer: str = Field(description="A clear, executive summary answering the user's IP or compliance query based strictly on the context.")
    confidence: int = Field(description="Confidence score from 0 to 100 based on how well the context answers the query.")
    applicable_ip_types: List[str] = Field(description="List of applicable IP protections (e.g., 'Process patent', 'Trade secret').")
    key_findings: List[str] = Field(description="3-5 bullet points of the most critical legal or prior-art findings.")
    next_steps: List[str] = Field(description="2-4 actionable recommended next steps for the user.")

def build_chat_response(query: str, jurisdiction: str, force_llm_failure: bool = False) -> ChatResponse:
    prior_art_store, legal_store = _get_vectorstores()
    
    evidence_items: List[EvidenceItem] = []
    contexts = []
    
    # --- 1A. Prior Art Retrieval & Reranking ---
    # Broad dense retrieval (top 15 candidates)
    pa_dense_results = prior_art_store.similarity_search_with_score(query, k=15)
    # Cross-encoder reranking (top 3)
    pa_reranked = rerank_documents(query, pa_dense_results, top_k=3)
    
    for idx, (doc, chroma_dist, rerank_score) in enumerate(pa_reranked):
        # Even with reranking, we can enforce a baseline threshold if needed,
        # but the reranker handles relevance well. We'll skip very low rerank scores (e.g., < -2.0)
        if rerank_score < -2.0:
            continue
            
        plant_family = doc.metadata.get("plant_family", "Unknown")
        source = doc.metadata.get("source", "Unknown")
        contexts.append(f"[PRIOR ART - {source}]: {doc.page_content}")
        
        evidence_items.append(
            EvidenceItem(
                id=f"ev_pa_{idx}",
                number=source,
                jurisdiction=doc.metadata.get("jurisdiction", "India"),
                risk="risk" if rerank_score > 0 else "review",
                title=f"Prior Art Record for {plant_family}",
                whyRelevant=f"Match (Rerank: {rerank_score:.2f} | L2: {chroma_dist:.2f}). {doc.page_content[:100]}..."
            )
        )

    # --- 1B. Legal Retrieval & Reranking ---
    if legal_store:
        try:
            legal_dense_results = legal_store.similarity_search_with_score(query, k=15)
            legal_reranked = rerank_documents(query, legal_dense_results, top_k=2)
            
            for idx, (doc, chroma_dist, rerank_score) in enumerate(legal_reranked):
                if rerank_score < -2.0:
                    continue
                source = doc.metadata.get("source", "Unknown")
                contexts.append(f"[LEGAL - {source}]: {doc.page_content}")
                
                evidence_items.append(
                    EvidenceItem(
                        id=f"ev_leg_{idx}",
                        number=source,
                        jurisdiction=doc.metadata.get("jurisdiction", "India"),
                        risk="info",
                        title=f"Legal/Compliance Rule from {source}",
                        whyRelevant=f"Match (Rerank: {rerank_score:.2f} | L2: {chroma_dist:.2f}). {doc.page_content[:100]}..."
                    )
                )
        except Exception as e:
            logging.warning(f"Skipping legal retrieval: {e}")

    # 2. Empty State Handling
    if not evidence_items:
        return ChatResponse(
            executive_answer="No relevant official records, prior art, or legal clauses were found matching your query in our current database.",
            confidence=40,
            source_agreement=0,
            jurisdiction_coverage=100,
            evidence_count=0,
            applicable_ip_types=["Further analysis needed"],
            key_findings=["No overlap with existing patents, TKDL records, or compliance laws in the current database."],
            next_steps=["Consult a human expert.", "Expand the search terms."],
            evidence=[]
        )

    # 3. LLM Generation
    combined_context = "\n\n".join(contexts)
    
    if LLM_PROVIDER and not force_llm_failure:
        try:
            if LLM_PROVIDER == "google":
                llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0, google_api_key=google_key)
            elif LLM_PROVIDER == "openai":
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            elif LLM_PROVIDER == "groq":
                llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)
            elif LLM_PROVIDER == "mistral":
                llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
                
            structured_llm = llm.with_structured_output(RAGAnalysisOutput)
            
            prompt = PromptTemplate.from_template(
                """You are an IP and Legal compliance AI assistant.
                Analyze the user's formulation or IP query based STRICTLY on the retrieved context below.
                Target Jurisdiction: {jurisdiction}
                
                Retrieved Context:
                {context}
                
                User Query: {query}
                
                Provide an executive summary, confidence score, applicable IP types, key findings, and next steps.
                Do NOT hallucinate. If the context does not fully answer the query, state the limitations clearly.
                """
            )
            
            chain = prompt | structured_llm
            result: RAGAnalysisOutput = chain.invoke({
                "jurisdiction": jurisdiction,
                "context": combined_context,
                "query": query
            })
            
            return ChatResponse(
                executive_answer=result.executive_answer,
                confidence=result.confidence,
                source_agreement=90,
                jurisdiction_coverage=100,
                evidence_count=len(evidence_items),
                applicable_ip_types=result.applicable_ip_types,
                key_findings=result.key_findings,
                next_steps=result.next_steps,
                evidence=evidence_items
            )
        except Exception as e:
            logging.error(f"LLM Generation failed: {e}")
            pass

    # 4. Fallback if LLM is unavailable or fails
    return ChatResponse(
        executive_answer=f"Evidence was retrieved ({len(evidence_items)} records), but LLM analysis is currently unavailable. Please review the attached evidence directly.",
        confidence=0,
        source_agreement=0,
        jurisdiction_coverage=100,
        evidence_count=len(evidence_items),
        applicable_ip_types=["Pending LLM Analysis"],
        key_findings=[f"Found relevant context in {ev.number} (L2: {ev.whyRelevant.split('L2: ')[1].split(')')[0]})" for ev in evidence_items[:3]],
        next_steps=["Review the attached evidence nodes.", "Configure API keys for full LLM synthesis."],
        evidence=evidence_items
    )
