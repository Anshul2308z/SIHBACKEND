import json
from sihbackend.services.chat_service import build_chat_response

def run_tests():
    print("=== Phase 3 RAG Pipeline Acceptance Tests ===\n")

    # 1. Known Neem/prior-art query
    print("Test 1: Known Neem query")
    res1 = build_chat_response("Neem extract for treating skin conditions like acne or psoriasis", "India")
    print(json.dumps(res1.model_dump(), indent=2))
    print("\n" + "="*50 + "\n")

    # 2. Legal material query
    print("Test 2: Legal material query")
    res2 = build_chat_response("What are the penalties under Section 3 of the Patents Act?", "India")
    print(json.dumps(res2.model_dump(), indent=2))
    print("\n" + "="*50 + "\n")

    # 3. Neem + Legal
    print("Test 3: Both (Neem + Legal)")
    res3 = build_chat_response("Is my neem skin formulation patentable under Indian law?", "India")
    print(json.dumps(res3.model_dump(), indent=2))
    print("\n" + "="*50 + "\n")

    # 4. Unrelated query (empty state)
    print("Test 4: Unrelated query (Empty State)")
    res4 = build_chat_response("How do I bake a chocolate cake?", "India")
    print(json.dumps(res4.model_dump(), indent=2))
    print("\n" + "="*50 + "\n")

    # 5. Specific patent/case-number
    print("Test 5: Specific patent/case-number query")
    res5 = build_chat_response("TKDL record 1212/DEL/2009 Neem", "India")
    print(json.dumps(res5.model_dump(), indent=2))
    print("\n" + "="*50 + "\n")

    # 6. Fallback path (simulated by not having key)
    # The key is currently absent, so all above tests used the fallback.
    # The output of Test 1-5 already demonstrates Test 6.

    # 7. LLM invocation failure
    print("Test 7: LLM Invocation Failure Fallback")
    # We can force the fallback by calling it with the force_llm_failure flag
    res7 = build_chat_response("Neem extract", "India", force_llm_failure=True)
    print(json.dumps(res7.model_dump(), indent=2))
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    run_tests()
