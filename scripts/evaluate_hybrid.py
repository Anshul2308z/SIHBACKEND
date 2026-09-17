import json
from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.rag.vectorstore import get_vectorstore
from sihbackend.rag.retriever import HybridRetriever

def check_success(doc, expected_source, expected_structure):
    if expected_source not in doc.metadata.get("filename", "") and expected_source not in doc.metadata.get("source", ""):
        return False
    if expected_structure:
        meta_keys = ["section", "article", "clause", "jurisdiction"]
        for key in meta_keys:
            if key in doc.metadata and str(expected_structure).lower() == str(doc.metadata[key]).lower():
                return True
        if str(expected_structure).lower() in doc.page_content.lower():
            return True
        return False
    return True

def run_eval(retriever, dataset, is_hybrid=False):
    top_1_hits = 0
    top_3_hits = 0
    top_5_hits = 0
    mrr_sum = 0.0
    
    results_map = {}
    
    for item in dataset:
        query = item["question"]
        expected_source = item["expected_source"]
        expected_structure = item["expected_structural_identifier"]
        
        if is_hybrid:
            results = retriever.search(query, debug=True)
        else:
            results = retriever.similarity_search(query, k=5)
            
        hit_rank = -1
        for rank, doc in enumerate(results):
            if check_success(doc, expected_source, expected_structure):
                hit_rank = rank + 1
                break
                
        if hit_rank > 0:
            if hit_rank == 1: top_1_hits += 1
            if hit_rank <= 3: top_3_hits += 1
            if hit_rank <= 5: top_5_hits += 1
            mrr_sum += 1.0 / hit_rank
            
        results_map[query] = {
            "rank": hit_rank,
            "results": results
        }
            
    total = len(dataset)
    return {
        "top_1": top_1_hits / total,
        "top_3": top_3_hits / total,
        "top_5": top_5_hits / total,
        "mrr": mrr_sum / total,
        "map": results_map
    }

def main():
    with open("tests/data/retrieval_eval.json", "r") as f:
        dataset = json.load(f)
        
    embeddings = get_embeddings_model()
    vectorstore = get_vectorstore(embeddings, "vectorstore/legal")
    hybrid = HybridRetriever(vectorstore, k=5, candidate_k=20, rrf_c=60)
    
    print("Running Baseline (Dense)...")
    baseline = run_eval(vectorstore, dataset, is_hybrid=False)
    
    print("Running Hybrid (BM25 + Dense + RRF)...")
    hybrid_res = run_eval(hybrid, dataset, is_hybrid=True)
    
    print("\n" + "="*50)
    print("EVALUATION RESULTS COMPARISON")
    print("="*50)
    print(f"{'Metric':<15} | {'Baseline':<10} | {'Hybrid':<10} | {'Delta':<10}")
    print("-" * 50)
    
    metrics = ["top_1", "top_3", "top_5", "mrr"]
    for m in metrics:
        b_val = baseline[m]
        h_val = hybrid_res[m]
        delta = h_val - b_val
        if m == "mrr":
            print(f"{m.upper():<15} | {b_val:.4f}     | {h_val:.4f}     | {delta:+.4f}")
        else:
            print(f"{m.upper():<15} | {b_val:.2%}    | {h_val:.2%}    | {delta:+.2%}")
            
    # Analyze changes
    failed_to_success = []
    success_to_failed = []
    rank_changes = []
    
    for item in dataset:
        q = item["question"]
        b_rank = baseline["map"][q]["rank"]
        h_rank = hybrid_res["map"][q]["rank"]
        
        if b_rank == -1 and h_rank > 0:
            failed_to_success.append(q)
        elif b_rank > 0 and h_rank == -1:
            success_to_failed.append(q)
        elif b_rank != h_rank:
            rank_changes.append((q, b_rank, h_rank))
            
    print("\n" + "="*50)
    print("QUERY DELTAS")
    print("="*50)
    print(f"Failed -> Success ({len(failed_to_success)}):")
    for q in failed_to_success: print(f"  + {q}")
    
    print(f"\nSuccess -> Failed ({len(success_to_failed)}):")
    for q in success_to_failed: print(f"  - {q}")
    
    print(f"\nRank Changed ({len(rank_changes)}):")
    for q, b, h in rank_changes: print(f"  ~ {q} (Rank {b} -> {h})")
    
    # Specific diagnostics
    diag_queries = [
        "What does Brazil require regarding genetic heritage?",
        "According to Article 10, what body is established for the parties?",
        "How are Genetic resources (GR) defined in the treaty?",
        "What is the fee to register a trademark in Brazil?",
        "What does Section 64 say about the revocation of patents?"
    ]
    
    print("\n" + "="*50)
    print("SPECIFIC DIAGNOSTICS (HYBRID)")
    print("="*50)
    
    for q in diag_queries:
        print(f"\nQuery: {q}")
        res = hybrid_res["map"][q]
        hit_rank = res["rank"]
        print(f"Final Status: {'PASS' if hit_rank > 0 else 'FAIL'} (Rank {hit_rank})")
        
        for i, doc in enumerate(res["results"]):
            m = doc.metadata
            struct = m.get("section") or m.get("article") or m.get("clause") or m.get("jurisdiction") or "none"
            is_table = m.get("is_table", False)
            print(f"  Rank {i+1} [V:{m.get('_debug_v_rank')} | B:{m.get('_debug_b_rank')}] -> Src: {m.get('filename')} | Struct: {struct} | Table: {is_table}")

if __name__ == "__main__":
    main()
