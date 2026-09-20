import sys
from src.sihbackend.api.formulation import analyze_formulation
from src.sihbackend.schemas.formulation import FormulationRequest

def test():
    req = FormulationRequest(
        product="Face Wash",
        classical="Yes",
        novelty="No",
        claim="Acne",
        route=""
    )
    try:
        res = analyze_formulation(req)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

test()
