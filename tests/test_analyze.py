import asyncio
from sihbackend.schemas.analysis import AnalysisRequest
from sihbackend.services.analysis import perform_analysis

def run():
    print("Starting analyze search")
    try:
        req = AnalysisRequest(query="neem patent", jurisdiction="India")
        res = perform_analysis(req)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()
