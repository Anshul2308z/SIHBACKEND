from fastapi import APIRouter
from langchain_core.prompts import PromptTemplate
from sihbackend.schemas.abs import AbsRequest, AbsResponse, AbsStatus
from sihbackend.services.chat_service import _get_vectorstores, LLM_PROVIDER
import logging

router = APIRouter(prefix="/api/v1/compliance", tags=["Compliance"])

@router.post("/abs", response_model=AbsResponse)
def check_abs_compliance(request: AbsRequest):
    _, legal_store = _get_vectorstores()
    
    # 1. Build a semantic query for the DB based on the ABS risk factors
    query = f"Biological Diversity Act Access and Benefit Sharing NBA approval for commercial utilization of {request.resource} from {request.origin}."
    
    contexts = []
    if legal_store:
        try:
            legal_results = legal_store.similarity_search_with_score(query, k=3)
            for doc, _ in legal_results:
                contexts.append(doc.page_content)
        except Exception as e:
            logging.warning(f"Skipping legal retrieval: {e}")
            
    combined_context = "\n\n".join(contexts)

    # 2. Invoke LLM for classification
    if LLM_PROVIDER:
        try:
            if LLM_PROVIDER == "google":
                from langchain_google_genai import ChatGoogleGenerativeAI
                import os
                llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0, google_api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
            elif LLM_PROVIDER == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                from langchain_groq import ChatGroq
                llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=2048)
            else:
                raise Exception(f"Unsupported LLM for structured output: {LLM_PROVIDER}")

            structured_llm = llm.with_structured_output(AbsResponse)
            
            prompt = PromptTemplate.from_template(
                """You are an Access and Benefit-Sharing (ABS) compliance expert focusing on India's Biological Diversity Act, 2002 and the Nagoya Protocol.
                Analyze the following biological resource usage scenario:
                
                Resource: {resource}
                Origin: {origin}
                Collection method: {collection}
                Associated Traditional Knowledge (TK) used: {tk}
                Commercial intention: {commercial}
                Patent application planned: {patent}
                Export market planned: {exportMarket}
                
                Retrieved Legal Context:
                {context}
                
                Determine the ABS risk level ('risk', 'review', or 'verified') and the required compliance frameworks. 
                Explain exactly why NBA approval is or isn't required in your reasoning.
                IMPORTANT: Be extremely concise to prevent token truncation.
                """
            )
            
            chain = prompt | structured_llm
            result = chain.invoke({
                "resource": request.resource,
                "origin": request.origin,
                "collection": request.collection,
                "tk": str(request.tk),
                "commercial": str(request.commercial),
                "patent": str(request.patent),
                "exportMarket": str(request.exportMarket),
                "context": combined_context
            })
            
            return result
            
        except Exception as e:
            logging.error(f"LLM ABS Cla ssification failed: {e}")
            
    # 3. Hardcoded Fallback logic mirroring the frontend if LLM fails
    score = 0
    if request.collection == "Wild-collected": score += 2
    if request.collection == "Unknown": score += 2
    if request.tk: score += 2
    if request.commercial: score += 1
    if request.patent: score += 1
    if request.exportMarket: score += 1
    
    if request.collection == "Unknown":
        status = AbsStatus(level="review", label="Review required")
    elif score >= 6:
        status = AbsStatus(level="risk", label="High — documentation likely required")
    elif score >= 4:
        status = AbsStatus(level="review", label="Medium — review required")
    else:
        status = AbsStatus(level="verified", label="Low — limited signals detected")
        
    framework = ["Biological Diversity Act, 2002", "ABS Regulations, 2014", "Nagoya Protocol"] if request.origin.lower() == "india" else ["Nagoya Protocol", "National ABS legislation of the country of origin"]
    
    reasoning = "Based on standard ABS framework heuristics. Since LLM analysis is temporarily unavailable, please consult the NBA portal directly for official guidance."
    
    return AbsResponse(
        status=status,
        framework=framework,
        reasoning=reasoning
    )
