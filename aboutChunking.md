# Chunking Architecture & Retrieval Strategy

## 1. Chunking Milestones Achieved

We successfully transitioned from a naive text-splitting approach to a highly sophisticated **Structure-Aware, Page-Level Chunking Pipeline**. 

*   **Semantic Hierarchies over Arbitrary Splits:** Instead of chopping text arbitrarily, the chunker dynamically identifies the document type (e.g., FSSAI, WIPO Treaty, Indian Law) and splits text based on native legal boundaries (`legal_section`, `legal_article`, `legal_clause`, `heading_numbered`).
*   **Rich Metadata Extraction:** As chunks are created, explicit structural identifiers are extracted and attached as Chroma metadata (e.g., `{"section": "64"}`, `{"article": "10"}`, `{"source_layer": "source_material"}`).
*   **Page-Level Table Routing:** We abandoned "all-or-nothing" document table extraction. Using `pdfplumber`, the system analyzes each page layout. Pure data tables (like fee schedules) are perfectly extracted as localized Key-Value pairs (`table_row_group`), while standard text remains prose.
*   **The "Conservative Fallback" for Layout Grids:** We implemented a critical safeguard recognizing that some legal PDFs use visual tables to format standard text (e.g., WIPO articles inside boxes). If a page has tables but contains strong legal markers (like "Article 10"), it falls back to prose extraction to prevent the text from being shredded by bounding-box filters.
*   **Context Preservation:** Every chunk is prefixed with `[Document Title]`, and split chunks inherit their parent heading context (e.g., `[continuation] Section 3`).

## 2. The Current Retrieval Bottleneck

Through our controlled experiments (Dense baseline vs. BM25 Hybrid vs. Metadata Filtering), we identified exactly why queries fail to hit the Top-1 spot:

1.  **The "Table Domination" Effect:** Extracting tables as dense key-value pairs inadvertently created hyper-concentrated chunks. Standard dense vector embeddings struggle to differentiate between a conceptual legal explanation of a rule and a dense table row that happens to share all the same keywords. 
2.  **Lexical Blindness:** Dense embeddings understand concepts but ignore strict constraints. A query asking for "Article 10" often returns "Article 12" if the language is conceptually similar. (Standard BM25 failed to fix this due to tokenization noise).
3.  **Metadata Extraction Gaps:** Our chunking logic occasionally misses metadata (e.g., failing to tag "Brazil" due to formatting variations, or failing to tag "Section 64" because the PDF grouped it as "Sections 63–66").

## 3. Proposed Improvements to Elevate Match Percentages

To push our Top-1 match rate well beyond the 60-65% range, we can attack the problem from two angles: **Chunking Refinements** and **Retrieval Enhancements**.

### A. Chunking & Metadata Refinements (Data Layer)
*   **Grouped-Section Expansion:** Update the chunking regex to detect ranged provisions (e.g., "Sections 63–66"). Instead of generating no metadata, the system should map all numbers in that range to the chunk, so querying "Section 64" successfully triggers the metadata filter.
*   **Robust Jurisdiction Extraction:** Refine the regex in `record_jurisdiction` to better capture country names like "Brazil" even when formatting (newlines, spaces) varies from the expected standard. 
*   **LLM-Assisted Chunk Tagging:** For critical documents, optionally pass chunks through an extremely fast, small LLM during ingestion to generate synthetic tags (e.g., extracting implicit entities that regex misses) before pushing to Chroma.

### B. Retrieval Algorithm Enhancements (Query Layer)
*   **Implement a Cross-Encoder Reranker (Highest Impact):** The most effective way to defeat the "Table Domination" effect. We use standard dense retrieval to fetch the top 15–20 candidates, then pass them through a cross-encoder model (e.g., Cohere Rerank, BGE-Reranker). Cross-encoders evaluate the query and the chunk *together*, allowing them to easily realize that a user asking for a "definition" wants the prose Article, not a fee table.
*   **Query-to-Strategy Routing:** Expand the Self-Querying parser to detect the *intent* of the user. If the user asks for a "fee", "cost", or "list", the LLM automatically applies a filter: `where={"is_table": True}`. If they ask for a "definition" or "rule", it applies `where={"is_table": False}`.
*   **Query Expansion (HyDE):** For vague queries with no explicit metadata (e.g., "How are genetic resources defined?"), use an LLM to generate a hypothetical answer first, then embed that hypothetical answer to search the vectorstore. This drastically bridges the vocabulary gap between a short user question and dense legal text.

---

**Summary of Current Status:**
The foundation (the chunked vectorstore) is structurally sound, highly granular, and metadata-rich. Our Self-Querying Metadata parser with Safe Fallback has proven we can exploit this metadata safely.
