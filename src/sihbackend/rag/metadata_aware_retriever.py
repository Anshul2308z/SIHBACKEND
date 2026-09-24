from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from sihbackend.rag.query_parser import LLMQueryParser

class MetadataAwareRetriever:
    def __init__(self, vectorstore: PineconeVectorStore, use_fallback: bool = True, k: int = 5):
        self.vectorstore = vectorstore
        self.use_fallback = use_fallback
        self.k = k
        self.parser = LLMQueryParser()
        
    def search(self, query: str) -> Tuple[List[Document], Dict[str, Any]]:
        # 1. Parse constraints
        constraints = self.parser.parse_constraints(query)
        
        log_info = {
            "query": query,
            "extracted_constraints": constraints,
            "attempted_filtered": False,
            "fallback_occurred": False
        }
        
        # 2. If no explicit constraints, normal dense retrieval
        if not constraints:
            results = self.vectorstore.similarity_search(query, k=self.k)
            return results, log_info
            
        # 3. If explicit constraints exist, attempt filtered retrieval
        log_info["attempted_filtered"] = True
        
        # Format constraints for Chroma (where dict)
        where_filter = {}
        for k, v in constraints.items():
            # Chroma filters need string keys and values (or dicts for operators)
            # We map multiple constraints directly as AND.
            where_filter[k] = v
            
        try:
            # Chroma allows multiple conditions if they are top-level key-values, treated as AND.
            # But wait, sometimes chroma requires $and. We'll use simple dict if 1 key, else $and.
            if len(where_filter) == 1:
                final_filter = where_filter
            else:
                final_filter = {"$and": [{k: v} for k, v in where_filter.items()]}
                
            filtered_results = self.vectorstore.similarity_search(query, k=self.k, filter=final_filter)
        except Exception as e:
            # In case of any chroma filter format error, treat as 0 results
            filtered_results = []
            
        # 4. If filtered retrieval returns zero results and fallback is enabled:
        if len(filtered_results) == 0:
            if self.use_fallback:
                log_info["fallback_occurred"] = True
                fallback_results = self.vectorstore.similarity_search(query, k=self.k)
                return fallback_results, log_info
            else:
                # Return empty if fallback is disabled (for the experiment configuration B)
                return [], log_info
                
        return filtered_results, log_info
