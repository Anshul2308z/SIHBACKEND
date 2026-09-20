from fastapi import APIRouter
from langchain_core.prompts import PromptTemplate
from sihbackend.schemas.formulation import FormulationRequest, FormulationResponse
from sihbackend.services.chat_service import _get_vectorstores, LLM_PROVIDER
import logging

router = APIRouter(prefix="/api/v1/analyze", tags=["Formulation"])

@router.post("/formulation", response_model=FormulationResponse)
def analyze_formulation(request: FormulationRequest):
    _, legal_store = _get_vectorstores()
    
    # 1. Build a semantic query based on the user's answers to fetch legal context
    query = f"Regulations and licensing route for {request.route} with {request.claim} and novelty {request.novelty}."
    
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
            elif LLM_PROVIDER == "groq":
                from langchain_groq import ChatGroq
                llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
            else:
                raise Exception(f"Unsupported LLM for structured output: {LLM_PROVIDER}")

            structured_llm = llm.with_structured_output(FormulationResponse)
            
            prompt = PromptTemplate.from_template(
                """You are an expert regulatory affairs consultant for the Indian Ayush and CDSCO sector.
                Analyze the provided product details and classify it into one of the following categories:
                - Cosmetic
                - Phytopharmaceutical
                - Ayurveda-Aahar / nutraceutical
                - Classical / generic Ayurvedic medicine
                - Patent / proprietary medicine
                
                Product description: {product}
                Classical conformity: {classical}
                Novelty/purification: {novelty}
                Label claim: {claim}
                Application route: {route}
                
                Use the retrieved legal context if helpful:
                {context}
                
                Provide the label, confidence score (0-100), reasoning, licensing route, relevant authorities, and applicable IP protections.
                Ensure your classification directly aligns with standard Indian regulatory frameworks.
                """
            )
            
            chain = prompt | structured_llm
            result = chain.invoke({
                "product": request.product,
                "classical": request.classical,
                "novelty": request.novelty,
                "claim": request.claim,
                "route": request.route,
                "context": combined_context
            })
            
            return result
            
        except Exception as e:
            logging.error(f"LLM Formulation Classification failed: {e}")
            
    # 3. Hardcoded Fallback logic mirroring the frontend if LLM fails
    if request.claim == "Cosmetic or external appearance benefit" or request.route == "Topical application":
        return FormulationResponse(
            label="Cosmetic",
            confidence=79,
            reasoning="An appearance-directed claim typically falls under cosmetics regulation rather than the Ayurvedic drug route.",
            route="Cosmetics licensing route",
            authorities=["CDSCO", "State licensing authority"],
            ip=["Trade mark", "Design (packaging)", "Trade secret (process)"]
        )
    if request.novelty == "Yes — purified single-molecule fraction":
        return FormulationResponse(
            label="Phytopharmaceutical",
            confidence=84,
            reasoning="A purified fraction with a therapeutic claim aligns with the phytopharmaceutical drug category.",
            route="Phytopharmaceutical drug route",
            authorities=["CDSCO", "Ministry of Ayush"],
            ip=["Composition patent", "Process patent", "Regulatory data"]
        )
    if request.claim == "Nutrition or wellness support" or request.route == "Food or beverage form":
        return FormulationResponse(
            label="Ayurveda-Aahar / nutraceutical",
            confidence=76,
            reasoning="A nutrition/wellness claim points to the Ayurveda-Aahar and nutraceutical framework.",
            route="Food / Ayurveda-Aahar route",
            authorities=["FSSAI", "Ministry of Ayush"],
            ip=["Trade mark", "Process patent", "Trade secret"]
        )
    if request.classical == "Yes — recipe and process follow a classical formulary":
        return FormulationResponse(
            label="Classical / generic Ayurvedic medicine",
            confidence=88,
            reasoning="A formulation matching a classical formulary is treated as a classical Ayurvedic medicine.",
            route="Classical Ayurvedic medicine licence",
            authorities=["Ministry of Ayush", "State licensing authority"],
            ip=["Trade mark", "Process know-how", "No composition novelty expected"]
        )
    
    return FormulationResponse(
        label="Patent / proprietary medicine",
        confidence=81,
        reasoning="A classical base with a modified composition and a therapeutic claim falls under patent or proprietary Ayurvedic medicine.",
        route="Patent / proprietary medicine licence",
        authorities=["Ministry of Ayush", "State licensing authority"],
        ip=["Trade mark", "Process know-how"]
    )
