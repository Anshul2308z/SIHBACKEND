import argparse
from sihbackend.rag.document_loader import load_pdf
from sihbackend.rag.chunker import chunk_documents
from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.rag.vectorstore import create_or_update_vectorstore

def main():
    PDF_PATH = "corpus/legal/international/international.pdf"
    PERSIST_DIR = "vectorstore/legal"

    print("1. Loading PDF...")
    documents = load_pdf(PDF_PATH)
    print(f"Loaded {len(documents)} pages")

    print("2. Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    print("3. Initializing embeddings...")
    embeddings = get_embeddings_model()

    print("4. Storing in vector database...")
    vectorstore = create_or_update_vectorstore(
        documents=chunks,
        embeddings=embeddings,
        persist_directory=PERSIST_DIR
    )
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
