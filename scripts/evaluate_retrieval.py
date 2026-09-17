import json
import os
import sys
from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.rag.vectorstore import get_vectorstore

def check_success(doc, expected_source, expected_structure):
    if expected_source not in doc.metadata.get("filename", "") and expected_source not in doc.metadata.get("source", ""):
        return False
        
    if expected_structure:
        # Check explicit metadata fields
        meta_keys = ["section", "article", "clause", "jurisdiction"]
        for key in meta_keys:
            if key in doc.metadata and str(expected_structure).lower() == str(doc.metadata[key]).lower():
                return True
                
        # Fallback to checking the text if it's a fallback table or missing metadata
        if str(expected_structure).lower() in doc.page_content.lower():
            return True
            
        return False
        
    return True

def main():
    with open("tests/data/retrieval_eval.json", "r") as f:
        dataset = json.load(f)
        
    print(f"Loaded {len(dataset)} evaluation questions.")
    
    # Show distribution
    dist = {}
    for item in dataset:
        source = item['expected_source']
        dist[source] = dist.get(source, 0) + 1
    print("Distribution:")
    for k, v in dist.items():
        print(f" - {k}: {v}")
        
    embeddings = get_embeddings_model()
    vectorstore = get_vectorstore(embeddings, "vectorstore/legal")
    
    top_1_hits = 0
    top_3_hits = 0
    top_5_hits = 0
    mrr_sum = 0.0
    
    successful_cases = []
    failed_cases = []
    
    for i, item in enumerate(dataset):
        query = item["question"]
        expected_source = item["expected_source"]
        expected_structure = item["expected_structural_identifier"]
        
        results = vectorstore.similarity_search(query, k=5)
        
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
            successful_cases.append((item, results, hit_rank))
        else:
            failed_cases.append((item, results))
            
    total = len(dataset)
    top_1_acc = top_1_hits / total
    top_3_acc = top_3_hits / total
    top_5_acc = top_5_hits / total
    mrr = mrr_sum / total
    
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    print(f"Total Queries: {total}")
    print(f"Top-1 Accuracy: {top_1_acc:.2%}")
    print(f"Top-3 Accuracy: {top_3_acc:.2%}")
    print(f"Top-5 Accuracy: {top_5_acc:.2%}")
    print(f"Mean Reciprocal Rank (MRR): {mrr:.4f}")
    
    print("\n" + "="*50)
    print("SAMPLE SUCCESSFUL RETRIEVALS")
    print("="*50)
    for item, results, rank in successful_cases[:3]:
        print(f"\nQUESTION: {item['question']}")
        print(f"EXPECTED: {item['expected_source']} | {item['expected_structural_identifier']}")
        print(f"PASS (Rank {rank})")
        
    print("\n" + "="*50)
    print("SAMPLE FAILED RETRIEVALS")
    print("="*50)
    for item, results in failed_cases[:3]:
        print(f"\nQUESTION: {item['question']}")
        print(f"EXPECTED: {item['expected_source']} | {item['expected_structural_identifier']}")
        print("FAIL (Not in top 5)")
        print("RETRIEVED (Top 1):")
        if results:
            print(f"  Source: {results[0].metadata.get('source')}")
            print(f"  Content: {results[0].page_content[:150]}...")
        else:
            print("  No results returned.")
            
if __name__ == "__main__":
    main()
import json
with open('/tmp/opencode/results.json', 'w') as f:
    json.dump(results_log, f)
