from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.rag.vectorstore import get_vectorstore
from sihbackend.rag.retriever import search_similar_documents

def main():
    PERSIST_DIR = "vectorstore/legal"

    print("1. Initializing embeddings...")
    embeddings = get_embeddings_model()

    print("2. Loading vector database...")
    vectorstore = get_vectorstore(
        embeddings=embeddings,
        persist_directory=PERSIST_DIR
    )

    questions = [
        "What does China require applicants to disclose?",
        "What requirements apply to patent rights involving Brazilian genetic heritage?",
        "What must a patent application disclose about biological material in Belgium?",
        "What documentation is required when an invention is based on genetic resources from an Andean Community member?"
    ]

    print("3. Querying...")
    for question in questions:
        print("=" * 80)
        print("QUESTION:", question)
        results = search_similar_documents(vectorstore, question, k=3)
        for result in results:
            print("PAGE:", result.metadata.get("page"))
            print(result.page_content[:500].replace('\n', ' '))
            print("-" * 80)

if __name__ == "__main__":
    main()
