from langchain_pinecone import PineconeVectorStore
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
import numpy as np
import hashlib

def search_similar_documents(vectorstore: PineconeVectorStore, query: str, k: int = 3) -> List[Document]:
    """Searches the vectorstore for documents similar to the query."""
    return vectorstore.similarity_search(query, k=k)

class HybridRetriever:
    def __init__(self, vectorstore: PineconeVectorStore, k: int = 5, candidate_k: int = 20, rrf_c: int = 60):
        self.vectorstore = vectorstore
        self.k = k
        self.candidate_k = candidate_k
        self.rrf_c = rrf_c
        
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            raise ImportError("Please install rank_bm25: uv add rank-bm25")
            
        # Extract all documents from the vectorstore for BM25 indexing
        db_data = self.vectorstore.get(include=["documents", "metadatas"])
        
        self.documents = []
        self.doc_hashes = []
        
        for i in range(len(db_data['documents'])):
            content = db_data['documents'][i]
            meta = db_data['metadatas'][i]
            doc = Document(page_content=content, metadata=meta)
            self.documents.append(doc)
            self.doc_hashes.append(self._hash_doc(doc))
            
        # Tokenize corpus for BM25 (simple whitespace/lower tokenizer)
        tokenized_corpus = [doc.page_content.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def _hash_doc(self, doc: Document) -> str:
        # Create a stable hash for a document to match across retrievers
        s = doc.page_content + str(doc.metadata.get("source", "")) + str(doc.metadata.get("page", ""))
        return hashlib.md5(s.encode()).hexdigest()

    def search(self, query: str, debug: bool = False) -> List[Document]:
        # 1. Vector Search
        vector_results = self.vectorstore.similarity_search(query, k=self.candidate_k)
        vector_ranks = {self._hash_doc(doc): rank for rank, doc in enumerate(vector_results)}
        
        # 2. BM25 Search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top candidate_k indices
        top_n = np.argsort(bm25_scores)[::-1][:self.candidate_k]
        bm25_results = [self.documents[i] for i in top_n]
        bm25_ranks = {self._hash_doc(doc): rank for rank, doc in enumerate(bm25_results)}
        
        # 3. Reciprocal Rank Fusion
        rrf_scores = {}
        all_docs = {}
        
        for doc in vector_results + bm25_results:
            dh = self._hash_doc(doc)
            all_docs[dh] = doc
            
        for dh, doc in all_docs.items():
            v_rank = vector_ranks.get(dh, 1000)
            b_rank = bm25_ranks.get(dh, 1000)
            
            v_score = 1.0 / (self.rrf_c + v_rank + 1) if dh in vector_ranks else 0.0
            b_score = 1.0 / (self.rrf_c + b_rank + 1) if dh in bm25_ranks else 0.0
            
            rrf_scores[dh] = v_score + b_score
            
        # Sort by fused score
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top k
        final_results = []
        for i, (dh, score) in enumerate(sorted_docs[:self.k]):
            doc = all_docs[dh]
            if debug:
                doc.metadata["_debug_rrf_score"] = score
                doc.metadata["_debug_v_rank"] = vector_ranks.get(dh, 1000) + 1
                doc.metadata["_debug_b_rank"] = bm25_ranks.get(dh, 1000) + 1
                doc.metadata["_debug_fused_rank"] = i + 1
            final_results.append(doc)
            
        return final_results
