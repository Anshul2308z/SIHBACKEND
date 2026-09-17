import pdfplumber
from typing import List, Dict, Any
from langchain_core.documents import Document

def load_tables_from_pdf(filepath: str, document_title: str) -> List[Document]:
    """Loads a PDF and extracts tables directly into semantic chunks."""
    documents = []
    
    with pdfplumber.open(filepath) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            # If no tables found, extract normal text for fallback
            if not tables:
                text = page.extract_text()
                if text and text.strip():
                    documents.append(Document(
                        page_content=text,
                        metadata={"source": filepath, "page": page_idx, "is_table": False, "title": document_title}
                    ))
                continue
                
            for table_idx, table in enumerate(tables):
                # Clean up table by removing empty rows
                cleaned_table = []
                for row in table:
                    if not row: continue
                    clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                    if any(clean_row):
                        cleaned_table.append(clean_row)
                        
                if len(cleaned_table) < 2:
                    continue # Need at least header + 1 row
                    
                headers = cleaned_table[0]
                
                # Each row becomes a chunk
                for row_idx, row in enumerate(cleaned_table[1:]):
                    # Align with headers
                    row_dict = {}
                    for col_idx, cell in enumerate(row):
                        header = headers[col_idx] if col_idx < len(headers) else f"Column {col_idx}"
                        header = header if header else f"Column {col_idx}"
                        row_dict[header] = cell
                        
                    # Format chunk content
                    content_lines = []
                    for k, v in row_dict.items():
                        if v: # Only include non-empty values
                            content_lines.append(f"{k}: {v}")
                            
                    if not content_lines:
                        continue
                        
                    chunk_text = "\n".join(content_lines)
                    
                    documents.append(Document(
                        page_content=chunk_text,
                        metadata={
                            "source": filepath,
                            "page": page_idx,
                            "is_table": True,
                            "title": document_title,
                            "table_idx": table_idx,
                            "row_idx": row_idx
                        }
                    ))
                    
    return documents
