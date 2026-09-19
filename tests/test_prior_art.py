import asyncio
from sihbackend.services.prior_art_service import build_prior_art_graph

def run():
    print("Starting prior art search")
    try:
        res = build_prior_art_graph("neem patent")
        print("Success:", res)
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    run()
