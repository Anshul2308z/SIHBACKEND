import os
import shutil
from typing import List, Optional
from langchain_chroma import Chroma

# Vercel Read-Only Filesystem Fix
VERCEL_ENV = os.environ.get("VERCEL") == "1"
BASE_VS_DIR = "/tmp/vectorstore" if VERCEL_ENV else "vectorstore"

if VERCEL_ENV and not os.path.exists(BASE_VS_DIR):
    try:
        shutil.copytree("vectorstore", BASE_VS_DIR)
    except Exception as e:
        print("Failed to copy vectorstore to /tmp:", e)

from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.schemas.prior_art import PriorArtGraphResponse, EvidenceNode
from sihbackend.services.reranker import rerank_documents

# Singleton pattern or global initialization can be refined later
# For now, we initialize on demand or at module level
_embeddings = None
_vectorstore = None

def _get_vectorstore():
    global _embeddings, _vectorstore
    if _vectorstore is None:
        _embeddings = get_embeddings_model()
        _vectorstore = Chroma(
            persist_directory=f"{BASE_VS_DIR}/prior_art",
            embedding_function=_embeddings
        )
    return _vectorstore

def build_prior_art_graph(query: Optional[str]) -> PriorArtGraphResponse:
    if not query:
        # If frontend sends no query, honestly return an empty graph
        return PriorArtGraphResponse(nodes=[], edges=[])

    vectorstore = _get_vectorstore()
    
    # 1. Retrieve relevant prior art (dense)
    dense_results = vectorstore.similarity_search_with_score(query, k=15)
    
    if not dense_results:
        return PriorArtGraphResponse(nodes=[], edges=[])

    # 2. Cross-Encoder Reranking
    reranked_results = rerank_documents(query, dense_results, top_k=5)

    nodes: List[EvidenceNode] = []
    edges: List[tuple[str, str]] = []
    
    # Root node representing the user's query/formulation
    formulation_id = "formulation_0"
    nodes.append(
        EvidenceNode(
            id=formulation_id,
            label="User Formulation",
            layer="formulation",
            passage=query
        )
    )
    
    # Process results into evidence nodes
    for idx, (doc, chroma_dist, rerank_score) in enumerate(reranked_results):
        # We only want relatively good matches. 
        if rerank_score < -2.0:
            continue
            
        metadata = doc.metadata
        plant_family = metadata.get("plant_family", "Unknown Plant")
        source_file = metadata.get("source", "Unknown Source")
        jurisdiction = metadata.get("jurisdiction", "Unknown")
        
        # Try to extract a case number if it's at the beginning (e.g. "1212/DEL/2009:")
        case_num = None
        content_preview = doc.page_content.replace(f"[Plant: {plant_family}]\n", "")
        if ":" in content_preview[:50]:
            possible_case = content_preview.split(":")[0].strip()
            if "/" in possible_case or "USPTO" in possible_case:
                case_num = possible_case
        
        node_id = f"evidence_{idx}"
        
        # Determine layer based on case number format
        layer = "patent"
        source_badge = "ipindia"
        if case_num and "USPTO" in case_num:
            layer = "international"
            source_badge = "uspto"
        elif "TKDL" in content_preview:
            layer = "tkdl"
            source_badge = "tkdl"
            
        nodes.append(
            EvidenceNode(
                id=node_id,
                label=f"{plant_family} Evidence",
                layer=layer,
                source=source_badge,
                jurisdiction=jurisdiction,
                caseNumber=case_num,
                passage=content_preview[:300] + "..." if len(content_preview) > 300 else content_preview,
                verification=f"Match (Rerank: {rerank_score:.2f} | L2: {chroma_dist:.2f}) from {source_file}"
            )
        )
        edges.append((formulation_id, node_id))

    return PriorArtGraphResponse(nodes=nodes, edges=edges)
