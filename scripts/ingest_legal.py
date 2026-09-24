from dotenv import load_dotenv
load_dotenv()
import os
import hashlib
from typing import List
from sihbackend.rag.document_loader import load_pdf
from sihbackend.rag.chunker import chunk_documents
from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.rag.vectorstore import create_or_update_vectorstore

IN_SCOPE_FILES = {
    "Ayurveda_Trademark_Act_IP_India_Summary.pdf",
    "fssai regulations.pdf",
    "full costs data.pdf",
    "Indian Law.pdf",
    "international laws,reg.pdf",
    "offices organisation .pdf",
    "wipo sources.pdf",
    "wipo treaty law.pdf"
}

def main():
    CORPUS_DIR = "corpus/"
    INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "sihbackend")
    NAMESPACE = "legal"
    
    # 1. Discover all in-scope PDFs
    all_pdfs = []
    for root, _, files in os.walk(CORPUS_DIR):
        for file in files:
            if file.endswith(".pdf") and file in IN_SCOPE_FILES:
                all_pdfs.append(os.path.join(root, file))
                
    all_documents = []
    for pdf_path in all_pdfs:
        print(f"Loading {pdf_path}...")
        docs = load_pdf(pdf_path)
        all_documents.extend(docs)
        
    print(f"Loaded {len(all_documents)} pages.")
    
    print("Chunking documents...")
    chunks = chunk_documents(all_documents)
    print(f"Created {len(chunks)} chunks.")
    
    print("Initializing embeddings...")
    embeddings = get_embeddings_model()
    
    print(f"Storing in Pinecone ({INDEX_NAME}, namespace: {NAMESPACE})...")
    create_or_update_vectorstore(
        documents=chunks,
        embeddings=embeddings,
        index_name=INDEX_NAME,
        namespace=NAMESPACE
    )
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
