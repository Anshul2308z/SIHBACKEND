from dotenv import load_dotenv
load_dotenv()
import os
import re
import pdfplumber
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.rag.vectorstore import create_or_update_vectorstore

def load_and_chunk_pdf(pdf_path: str) -> List[Document]:
    filename = os.path.basename(pdf_path)
    plant_family = os.path.splitext(filename)[0]
    
    docs = []
    
    # 1. Regex pattern for patent/TKDL records (e.g., "1212/DEL/2009:" or "20130017279 / USPTO:")
    patent_pattern = re.compile(r'\n(?=\d+(?:/[A-Z]+/\d+|\s*/\s*USPTO)\s*:)', re.IGNORECASE)
    
    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            text = page.extract_text()
            if not text:
                continue
                
            # Try splitting by patent record regex first
            parts = patent_pattern.split(text)
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                    
                # If part is large, use the fallback recursive splitter
                if len(part) > 1500:
                    sub_chunks = fallback_splitter.split_text(part)
                    for sc in sub_chunks:
                        docs.append(Document(
                            page_content=f"[Plant: {plant_family.title()}]\n{sc}",
                            metadata={
                                "source": filename,
                                "page": page_num,
                                "document_type": "prior_art",
                                "jurisdiction": "India", # Defaulting to India for this corpus
                                "plant_family": plant_family.title()
                            }
                        ))
                else:
                    docs.append(Document(
                        page_content=f"[Plant: {plant_family.title()}]\n{part}",
                        metadata={
                            "source": filename,
                            "page": page_num,
                            "document_type": "prior_art",
                            "jurisdiction": "India",
                            "plant_family": plant_family.title()
                        }
                    ))
    return docs

def main():
    # Allow passing target dir as env variable or use default
    target_dir = os.environ.get("PRIOR_ART_DIR", os.path.expanduser("~/Desktop/toChunk/today/family/"))
    INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "sihbackend")
    NAMESPACE = "prior_art"
    
    print(f"Target Directory: {target_dir}")
    if not os.path.exists(target_dir):
        print(f"Error: Directory {target_dir} does not exist.")
        return

    # Discover PDFs
    pdf_files = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDFs")
    
    all_chunks = []
    total_pages_approx = 0
    
    for pdf_path in pdf_files:
        try:
            chunks = load_and_chunk_pdf(pdf_path)
            all_chunks.extend(chunks)
            # Estimate pages (using the max page number found in chunks metadata for this file)
            pages = set(c.metadata["page"] for c in chunks)
            total_pages_approx += len(pages)
        except Exception as e:
            print(f"Failed to process {pdf_path}: {e}")

    print(f"Loaded {len(pdf_files)} documents")
    print(f"Extracted ~{total_pages_approx} pages")
    print(f"Created {len(all_chunks)} chunks")
    
    if not all_chunks:
        print("No chunks created. Exiting.")
        return

    print("Embedding chunks...")
    embeddings = get_embeddings_model()
    
    print(f"Persisting {len(all_chunks)} vectors to Pinecone ({INDEX_NAME}, namespace: {NAMESPACE})...")
    create_or_update_vectorstore(
        documents=all_chunks,
        embeddings=embeddings,
        index_name=INDEX_NAME,
        namespace=NAMESPACE
    )
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
