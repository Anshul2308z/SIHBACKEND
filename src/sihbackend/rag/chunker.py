import re
import os
import pdfplumber
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentClassifier:
    @staticmethod
    def classify(text: str, filename: str) -> str:
        text_start = text[:2000].lower()
        fname = filename.lower()
        
        if "fssai" in fname or "खाद्य" in text_start:
            return "legal_clause"
        elif "indian law" in fname or "patent & trademark laws" in text_start:
            return "legal_section"
        elif "international laws,reg" in fname or "international ayurvedic patent law data" in text_start:
            return "record_jurisdiction"
        elif "wipo treaty law" in fname or "gratk treaty" in text_start:
            return "legal_article"
        elif "ayurveda_trademark_act" in fname or "trade marks for ayurvedic products" in text_start:
            return "heading_numbered"
        
        return "fallback"

class StructureAwareChunker:
    def __init__(self):
        self.fallback_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    def _get_document_title(self, filepath: str) -> str:
        base = os.path.basename(filepath)
        name, _ = os.path.splitext(base)
        return name.replace("_", " ").strip()

    def _determine_page_type(self, page, prose_strategy: str) -> str:
        tables = page.find_tables()
        if not tables:
            return "prose"
            
        text = page.extract_text() or ""
        
        is_structural = False
        if prose_strategy == "legal_section":
            is_structural = bool(re.search(r'(?:Section|Chapter)\s+\d+', text, re.IGNORECASE))
        elif prose_strategy == "legal_article":
            is_structural = bool(re.search(r'Article\s+\d+', text, re.IGNORECASE))
        elif prose_strategy == "record_jurisdiction":
            is_structural = bool(re.search(r'\n*\d+\s+[A-Z]', text))
        elif prose_strategy in ["heading_numbered", "legal_clause"]:
            is_structural = bool(re.search(r'\n*\d+\.\s+', text))
            
        if is_structural:
            return "mixed"
        return "table"

    def _process_page_layout(self, page, pdf_path: str, doc_title: str, page_num: int, prose_strategy: str) -> Tuple[str, List[Document], str]:
        page_type = self._determine_page_type(page, prose_strategy)
        
        if page_type == "prose":
            return page.extract_text() or "", [], "prose"
            
        elif page_type == "mixed":
            # CONSERVATIVE FALLBACK:
            # Region-level extraction with bounding boxes destroys visual layout grids (like WIPO Articles).
            # If a page has tables but is primarily structural, we treat the entire page as prose 
            # to preserve the structure-aware chunking strategies instead of shredding it.
            return page.extract_text() or "", [], "mixed"
            
        else: # table
            tables = page.find_tables()
            table_chunks = []
            
            for table_idx, table_obj in enumerate(tables):
                extracted = table_obj.extract()
                if not extracted or len(extracted) < 2: continue
                
                headers = extracted[0]
                for row_idx, row in enumerate(extracted[1:]):
                    if not row or not any(row): continue
                    
                    row_dict = {}
                    for col_idx, cell in enumerate(row):
                        header = str(headers[col_idx]).replace('\n', ' ').strip() if col_idx < len(headers) and headers[col_idx] else f"Column {col_idx}"
                        val = str(cell).replace('\n', ' ').strip() if cell else ""
                        if val:
                            row_dict[header] = val
                            
                    content_lines = [f"{k}: {v}" for k, v in row_dict.items()]
                    if not content_lines: continue
                    
                    chunk_text = f"[{doc_title}]\n" + "\n".join(content_lines)
                    table_chunks.append(Document(
                        page_content=chunk_text,
                        metadata={
                            "source": pdf_path,
                            "filename": os.path.basename(pdf_path),
                            "page": page_num,
                            "is_table": True,
                            "title": doc_title,
                            "table_idx": table_idx,
                            "row_idx": row_idx,
                            "strategy": "table_row_group",
                            "document_type": "table_data"
                        }
                    ))

            # Extract remaining prose outside tables for pure table pages
            bboxes = [t.bbox for t in tables]
            def not_in_bboxes(obj):
                if "top" not in obj or "bottom" not in obj: return True
                for (x0, top, x1, bottom) in bboxes:
                    if obj["top"] >= (top - 2) and obj["bottom"] <= (bottom + 2):
                        return False
                return True
                
            filtered_page = page.filter(not_in_bboxes)
            prose_text = filtered_page.extract_text() or ""
            
            return prose_text, table_chunks, "table"

    def chunk(self, docs: List[Document]) -> List[Document]:
        if not docs: return []
            
        from collections import defaultdict
        docs_by_source = defaultdict(list)
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            docs_by_source[source].append(doc)
            
        all_chunks = []
        
        for source, file_docs in docs_by_source.items():
            full_text_heuristic = "\n".join([d.page_content for d in file_docs])
            prose_strategy = DocumentClassifier.classify(full_text_heuristic, source)
            doc_title = self._get_document_title(source)
            
            combined_prose_text = ""
            page_map = []
            current_len = 0
            
            if os.path.exists(source):
                try:
                    with pdfplumber.open(source) as pdf:
                        for page_idx, page in enumerate(pdf.pages):
                            page_num = page_idx + 1
                            prose_text, table_chunks, page_type = self._process_page_layout(page, source, doc_title, page_num, prose_strategy)
                            
                            all_chunks.extend(table_chunks)
                            
                            if prose_text:
                                prose_with_nl = prose_text + "\n\n"
                                combined_prose_text += prose_with_nl
                                page_map.append((current_len, current_len + len(prose_with_nl), page_num))
                                current_len += len(prose_with_nl)
                except Exception as e:
                    print(f"Failed to process {source} with pdfplumber: {e}")
                    for d in file_docs:
                        text = d.page_content + "\n\n"
                        combined_prose_text += text
                        page_num = d.metadata.get("page", 0)
                        page_map.append((current_len, current_len + len(text), page_num))
                        current_len += len(text)
            else:
                for d in file_docs:
                    text = d.page_content + "\n\n"
                    combined_prose_text += text
                    page_num = d.metadata.get("page", 0)
                    page_map.append((current_len, current_len + len(text), page_num))
                    current_len += len(text)
                
            if combined_prose_text.strip():
                prose_chunks = self._apply_strategy(combined_prose_text, prose_strategy, doc_title, source, page_map)
                all_chunks.extend(prose_chunks)
            
        return all_chunks

    def _get_page(self, start_idx: int, page_map: List[tuple]) -> int:
        for start, end, page in page_map:
            if start <= start_idx < end:
                return page
        return 0

    def _apply_strategy(self, text: str, strategy: str, doc_title: str, source: str, page_map: List[tuple]) -> List[Document]:
        chunks = []
        doc_type_map = {
            "legal_section": "patent_act_summary",
            "legal_article": "treaty",
            "record_jurisdiction": "jurisdiction_dataset",
            "heading_numbered": "legal_summary_guide",
            "legal_clause": "regulatory_rules",
            "fallback": "document"
        }
        doc_type = doc_type_map.get(strategy, "document")
        
        if strategy == "legal_section":
            pattern = r'(\n(?:Section|Chapter)\s+\d+[^\n]*)'
            parts = re.split(pattern, text, flags=re.IGNORECASE)
        elif strategy == "legal_article":
            pattern = r'(\nArticle\s+\d+[^\n]*)'
            parts = re.split(pattern, text, flags=re.IGNORECASE)
        elif strategy == "heading_numbered":
            pattern = r'(\n\d+\.\s+[A-Z][^\n]*)'
            parts = re.split(pattern, text)
        elif strategy == "record_jurisdiction":
            pattern = r'(\n\d+\n[A-Z][a-z]+[^\n]*)'
            parts = re.split(pattern, text)
        elif strategy == "legal_clause":
             pattern = r'(\n\d+\.\s+[^\n]*)'
             parts = re.split(pattern, text)
        else:
             parts = [text]

        if len(parts) > 1:
            current_chunk = parts[0]
            current_idx = 0
            
            for i in range(1, len(parts), 2):
                if current_chunk.strip():
                    page = self._get_page(current_idx, page_map)
                    chunks.append(self._create_doc(current_chunk, doc_title, source, page, strategy, doc_type))
                
                header = parts[i]
                content = parts[i+1] if i+1 < len(parts) else ""
                current_chunk = header + content
                current_idx += len(header) + len(content)
                
            if current_chunk.strip():
                page = self._get_page(current_idx, page_map)
                chunks.append(self._create_doc(current_chunk, doc_title, source, page, strategy, doc_type))
        else:
             chunks.append(self._create_doc(text, doc_title, source, 0, "fallback", doc_type))
             
        final_chunks = []
        for c in chunks:
            content_text = c.page_content
            header_context = None
            
            if strategy == "legal_section":
                match = re.search(r'(Section\s+\d+[A-Z]*)', content_text, re.IGNORECASE)
                if match:
                    c.metadata["section"] = match.group(1).split()[-1]
                    header_context = match.group(1)
            elif strategy == "legal_article":
                match = re.search(r'(Article\s+\d+)', content_text, re.IGNORECASE)
                if match:
                    c.metadata["article"] = match.group(1).split()[-1]
                    header_context = match.group(1)
                    
                if "wipo" in source.lower():
                    if "Rule / content" in content_text:
                        c.metadata["source_layer"] = "source_material"
                    elif "IP-SAKTI implementation" in content_text:
                        c.metadata["source_layer"] = "project_interpretation"
                    elif "Ayurvedic interpretation" in content_text:
                        c.metadata["source_layer"] = "ayurvedic_interpretation"
                        
            elif strategy == "record_jurisdiction":
                match = re.search(r'^\n*\d+\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', content_text)
                if match:
                    c.metadata["jurisdiction"] = match.group(1).strip()
                    header_context = match.group(1).strip()
            elif strategy == "legal_clause":
                match = re.search(r'^\n*(\d+\.)\s+', content_text)
                if match:
                    c.metadata["clause"] = match.group(1).replace(".", "")
                    header_context = f"Clause {match.group(1)}"
            
            if len(c.page_content) > 3000:
                sub_chunks = self.fallback_splitter.split_documents([c])
                for idx, sc in enumerate(sub_chunks):
                    prefix = f"[{doc_title}]"
                    if idx > 0 and header_context:
                        prefix += f"\n{header_context}\n[continuation]"
                    sc.page_content = f"{prefix}\n{sc.page_content.strip()}"
                final_chunks.extend(sub_chunks)
            else:
                c.page_content = f"[{doc_title}]\n{c.page_content.strip()}"
                final_chunks.append(c)
                
        return final_chunks

    def _create_doc(self, text: str, title: str, source: str, page: int, strategy: str, doc_type: str) -> Document:
        return Document(
            page_content=text,
            metadata={
                "source": source,
                "filename": os.path.basename(source),
                "title": title,
                "page": page,
                "strategy": strategy,
                "document_type": doc_type
            }
        )

def chunk_documents(documents: List[Document]) -> List[Document]:
    chunker = StructureAwareChunker()
    return chunker.chunk(documents)
