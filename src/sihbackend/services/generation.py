import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from sihbackend.schemas.analysis import AnalysisResponse

SYSTEM_PROMPT = """You are a strictly grounded legal and IP analysis generator.
Your sole purpose is to answer the user's query using ONLY the provided retrieved context.

RULES:
- Answer ONLY from the retrieved context.
- Do not invent facts, legal provisions, requirements, dates, penalties, jurisdictions, or sources.
- Do not use general model knowledge to fill missing information.
- If the retrieved context does not contain enough information to answer the question, explicitly say that the available retrieved evidence is insufficient in your answer, and set risk_level to "unknown".
- Do not treat absence from the retrieved context as proof that something does not exist.
- Distinguish legal/source material from interpretive material based on the 'Source Layer' metadata provided.
- Do not silently merge contradictory information. If sources disagree or evidence is incomplete, state that clearly.
- Preserve uncertainty where the retrieved evidence is uncertain.
- Do not fabricate citations or source URLs.
- Every factual/legal claim should be traceable to the supplied retrieved context.
- Do not claim that a retrieved chunk is authoritative merely because it was retrieved.
- Do not provide legal certainty beyond what the supplied evidence supports.
- You are an ANALYSIS GENERATOR, not a legal authority. Do not say "According to the law..." unless the supplied context actually supports that statement.

SCHEMA INSTRUCTIONS:
- risk_level: Must be exactly one of: "low", "medium", "high", "unknown". If evidence is insufficient to make a defensible risk assessment, output "unknown". Do not infer "low risk" simply because no prohibition was retrieved.
- key_requirements: Extract only requirements explicitly supported by the retrieved context.
- relevant_jurisdictions: Only include jurisdictions supported by the content or reliable metadata. Do not infer.
- sources: Extract sources strictly from the metadata provided in the context blocks. Format as a string, e.g., "Document: [filename], Page: [page], Section: [section]". Do NOT invent URLs or fake citations.
- caveats: Explicitly mention meaningful limitations (e.g., insufficient retrieved evidence, source is interpretive, conflicting info).

CONTEXT:
{context}
"""

def format_documents(docs: List[Document]) -> str:
    formatted_chunks = []
    for i, doc in enumerate(docs):
        metadata = doc.metadata
        
        # Build the source string block deterministically
        lines = [f"--- SOURCE {i+1} ---"]
        
        # Handle filename or source_document
        doc_name = metadata.get("filename", metadata.get("source_document", "Unknown Document"))
        lines.append(f"Document: {doc_name}")
        
        if "page" in metadata:
            lines.append(f"Page: {metadata['page']}")
        if "section" in metadata:
            lines.append(f"Section: {metadata['section']}")
        if "article" in metadata:
            lines.append(f"Article: {metadata['article']}")
        if "clause" in metadata:
            lines.append(f"Clause: {metadata['clause']}")
        if "jurisdiction" in metadata:
            lines.append(f"Jurisdiction: {metadata['jurisdiction']}")
        if "source_layer" in metadata:
            lines.append(f"Source Layer: {metadata['source_layer']}")
        if "source_url" in metadata:
            lines.append(f"Source URL: {metadata['source_url']}")
            
        lines.append("Content:")
        lines.append(doc.page_content.strip())
        
        formatted_chunks.append("\n".join(lines))
        
    return "\n\n".join(formatted_chunks)

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "").lower()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    if provider == "openai":
        return ChatOpenAI(model=model, temperature=0)
    elif provider == "google":
        return ChatGoogleGenerativeAI(model=model, temperature=0)
    else:
        # Mock LLM behavior if no provider is configured, to ensure system stability
        return None

def generate_answer(query: str, retrieved_documents: List[Document]) -> AnalysisResponse:
    if not retrieved_documents:
        return AnalysisResponse(
            answer="There is insufficient retrieved evidence to answer the query.",
            risk_level="unknown",
            key_requirements=[],
            relevant_jurisdictions=[],
            sources=[],
            caveats=["No relevant documents were retrieved from the legal corpus."]
        )
        
    context = format_documents(retrieved_documents)
    
    llm = get_llm()
    if llm is None:
        # Mock response when LLM is unavailable to handle failure cleanly
        return AnalysisResponse(
            answer="LLM is not configured. This is a fallback response. Query received: " + query,
            risk_level="unknown",
            key_requirements=[],
            relevant_jurisdictions=[],
            sources=["Mock Source"],
            caveats=["LLM Provider not configured. Falling back to mock generation."]
        )
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{query}")
    ])
    
    try:
        chain = prompt | llm.with_structured_output(AnalysisResponse)
        response = chain.invoke({"context": context, "query": query})
        return response
    except Exception as e:
        return AnalysisResponse(
            answer=f"An error occurred during generation: {str(e)}",
            risk_level="unknown",
            key_requirements=[],
            relevant_jurisdictions=[],
            sources=[],
            caveats=["Generation service failure."]
        )
