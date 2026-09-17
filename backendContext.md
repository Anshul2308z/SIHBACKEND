# SIH Backend - Handoff Context & API Contract

This document provides the definitive, implementation-accurate state of the SIH Backend as of the current phase. It is intended for frontend developers and agents to understand the backend architecture, exact API structures, and data flows.

---

## 1. Project Purpose & Current Architecture
The SIH Backend is a Retrieval-Augmented Generation (RAG) system built to analyze IP risks, specifically regarding botanical formulations and traditional knowledge (TKDL).

**Current Architecture:**
*   **API Layer:** FastAPI exposing REST endpoints.
*   **Vector Database:** Local ChromaDB holding dense embeddings of prior art (patents, TKDL records) and legal regulations.
*   **Relational Database:** SQLAlchemy (SQLite/PostgreSQL) for user history and reference data.
*   **RAG Pipeline:** LangChain orchestrates retrieval, cross-encoder reranking, and Gemini LLM invocation to synthesize context-grounded IP risk reports without hallucinations.

## 2. Tech Stack & Dependencies
*   **Web Framework:** FastAPI
*   **Data Validation:** Pydantic
*   **ORM:** SQLAlchemy (Default: SQLite, Postgres-ready)
*   **Vector Database:** Chroma (via `langchain-chroma`)
*   **Orchestration:** LangChain
*   **LLM Engine:** Google Gemini (`gemini-3.6-flash` via `langchain-google-genai`)
*   **Cross-Encoder / Reranker:** `BAAI/bge-reranker-base` via `sentence-transformers`
*   **Package Management:** `uv`

---

## 3. Implemented API Endpoints

### A. Chat Message (RAG Analysis)
*   **Method:** `POST`
*   **Path:** `/api/v1/chat/message`
*   **Request Body:** `ChatRequest` (JSON)
    *   `query` (string, required): The user's query or formulation.
    *   `jurisdiction` (string, optional): Default `"India"`.
*   **Response:** `ChatResponse` (JSON)

### B. Prior Art Graph
*   **Method:** `POST`
*   **Path:** `/api/v1/prior-art/graph`
*   **Request Body:** `PriorArtGraphRequest` (JSON)
    *   `query` (string, optional): The user's query/formulation keywords.
*   **Response:** `PriorArtGraphResponse` (JSON)
    *   *Empty State:* If `query` is null/empty or no results are found, returns `{"nodes": [], "edges": []}`.

### C. Health Check
*   **Method:** `GET`
*   **Path:** `/health`
*   **Response:** `{"status": "ok"}`

*(Note: `/api/v1/analyze` exists in the router but is currently a stub/passthrough and should not be relied upon for the core RAG flow).*

---

## 4. Pydantic Request & Response Models

```json
// ChatRequest
{
  "query": "string",
  "jurisdiction": "string (optional, default: India)"
}

// ChatResponse
{
  "executive_answer": "string",
  "confidence": "integer (0-100)",
  "source_agreement": "integer (0-100)",
  "jurisdiction_coverage": "integer (0-100)",
  "evidence_count": "integer",
  "applicable_ip_types": ["string"],
  "key_findings": ["string"],
  "next_steps": ["string"],
  "evidence": ["EvidenceItem"] // See Section 5
}

// PriorArtGraphRequest
{
  "query": "string (optional)"
}

// PriorArtGraphResponse
{
  "nodes": ["EvidenceNode"], // See Section 5
  "edges": [
     ["string_source_id", "string_target_id"]
  ]
}
```

---

## 5. Evidence Data Structures

**`EvidenceItem` (Used in ChatResponse):**
```json
{
  "id": "ev_pa_0",
  "number": "neem.pdf",
  "jurisdiction": "India",
  "risk": "risk", // or "info", "review"
  "title": "Prior Art Record for Neem",
  "whyRelevant": "Match (Rerank: 0.97 | L2: 0.63). [Excerpt text...]"
}
```

**`EvidenceNode` (Used in PriorArtGraphResponse):**
```json
{
  "id": "evidence_0",
  "label": "Neem Evidence",
  "layer": "patent", // e.g., 'formulation', 'tkdl', 'patent', 'international'
  "source": "ipindia", // e.g., 'ipindia', 'uspto', 'tkdl'
  "jurisdiction": "India", // Optional
  "caseNumber": "1212/DEL/2009", // Optional
  "outcome": null, // Optional
  "sourceDate": null, // Optional
  "verification": "Match (Rerank: 0.97 | L2: 0.63) from neem.pdf",
  "passage": "[Excerpt text...]"
}
```

---

## 6. The `/api/v1/chat/message` Data Flow
1.  **Request:** Frontend sends `query` and `jurisdiction`.
2.  **Chroma Dense Retrieval:** Backend queries both `prior_art` and `legal` Chroma collections independently, fetching `k=15` candidates each using L2 distance.
3.  **Cross-Encoder Reranking:** The 15 candidates are evaluated by `BAAI/bge-reranker-base`. It scores their true semantic relevance to the query, filters out poor matches (score < -2.0), and keeps the top 3 (prior art) and top 2 (legal).
4.  **Context Construction:** The reranked documents are formatted into context strings and mapped to `EvidenceItem` objects.
5.  **Gemini LLM Synthesis:** A strict structured prompt instructs Gemini to read the context and output a Pydantic `RAGAnalysisOutput`. It is barred from answering using external knowledge.
6.  **Response:** The structured LLM output and the raw `EvidenceItems` are merged into the final `ChatResponse` and returned.

## 7. The `/api/v1/prior-art/graph` Flow
1.  **Request:** Frontend sends a `query`.
2.  **Early Exit:** If the query is empty/null, returns empty nodes/edges immediately.
3.  **Chroma Dense Retrieval:** Queries `prior_art` collection for `k=15` candidates.
4.  **Cross-Encoder Reranking:** Filters and reranks to the top `k=5`.
5.  **Graph Construction:** 
    *   Creates a root `formulation` node representing the user's query.
    *   Iterates through reranked results, creating `EvidenceNode` objects.
    *   Determines `layer` and `source` badge by inspecting the document text (e.g., looking for "TKDL" or "USPTO").
    *   Creates edges linking the root node to the evidence nodes.
6.  **Response:** Returns the JSON graph structure.

---

## 8. Meaning of Evidence Fields & Metadata

*   **`source` / `number`:** The origin file (e.g., `neem.pdf` or `fssai regulations.pdf`).
*   **`plant_family`:** The botanical subject of the document (extracted via ingestion scripts into Chroma metadata).
*   **`jurisdiction`:** Geographic scope (e.g., "India").
*   **`layer`:** Node categorization in the graph (e.g., `tkdl`, `patent`, `international`).
*   **`risk`:** Risk categorization (e.g., `risk` for prior art conflicts, `info` for legal compliance).
*   **`Chroma L2 distance`:** The initial dense vector distance. **Lower is better (closer match).** This is a *distance* metric, not a similarity score.
*   **`Cross-encoder/Rerank score`:** The secondary model's evaluation of relevance. **Higher is better.** 
*   **`whyRelevant` / `verification`:** A formatted string containing the Rerank Score, the L2 distance, and an excerpt of the text. Crucial for tracing why the LLM made a claim.

---

## 9. Failure & Empty State Behaviors

*   **No Retrieval Results:** If Chroma finds nothing (or the reranker filters everything out), the API returns a graceful empty state: `confidence: 40`, `evidence: []`, and a summary stating no records were found.
*   **Gemini Unavailable / Invocation Failure:** If the API key is missing, rate limits hit (e.g., `503 UNAVAILABLE`), or the LLM fails to output valid JSON, the backend catches the error. It returns a **Fallback State**: `confidence: 0`, `executive_answer` indicating the LLM is unavailable, but **still includes the retrieved `evidence` array** so the user isn't completely blocked.
*   **Malformed Requests:** FastAPI automatically returns standard `422 Unprocessable Entity` for invalid Pydantic schemas.
*   **Legal Vectorstore Missing:** If the `legal` vectorstore isn't initialized, the backend gracefully skips it and relies only on `prior_art`.

---

## 10. Relational Persistence Layer

*   **Database Config:** Managed in `src/sihbackend/db/database.py`. Defaults to `sqlite:///./sih_application.db` (auto-created on run). Fully PostgreSQL-ready if `POSTGRES_URL` is set in the environment.
*   **Models (`src/sihbackend/db/models.py`):**
    1.  `UserSession`: Stores `user_id`, `query`, `jurisdiction`, `report_data` (JSON), and timestamps.
    2.  `Plant`: Botanical reference data (e.g., TKDL status).
    3.  `Source`: Registry of authorities (USPTO, IPIndia).
    4.  `Jurisdiction`: Patent durations, regulators.
*   **Current Usage:** The models and DB connection are defined, but the endpoints **do not currently write** history or read reference data during the RAG flow. This is a framework for future integration. 

---

## 11. Chroma Collections

*   **Path:** Stored locally in `vectorstore/`.
*   **`prior_art` Collection:** Contains chunked patent applications and TKDL entries (e.g., `corpus/neem.pdf`). Metadata includes `plant_family`, `source`, `jurisdiction`.
*   **`legal` Collection:** Contains chunked statutory acts and regulations (e.g., `corpus/Indian Law.pdf`).
*   **Ingestion:** Performed via offline scripts (`scripts/ingest_prior_art.py`). Vector databases are read-only during normal API operation.

---

## 12. Required Environment Variables

*   **`ACTIVE_LLM`**: Explicitly controls which LLM provider to use. Available values:
    *   `"google"`: Uses Gemini 3.6 Flash (default). Requires `GEMINI_API_KEY`.
    *   `"openai"`: Uses gpt-4o-mini. Requires `OPENAI_API_KEY`.
    *   `"groq"`: Uses Llama-3.1-70b. Requires `GROQ_API_KEY`.
    *   `"mistral"`: Uses Mistral Large. Requires `MISTRAL_API_KEY`.
*   **`GEMINI_API_KEY`** or **`GOOGLE_API_KEY`**: Required if `ACTIVE_LLM="google"`.
*   **`OPENAI_API_KEY`**: Required if `ACTIVE_LLM="openai"`.
*   **`GROQ_API_KEY`**: Required if `ACTIVE_LLM="groq"`.
*   **`MISTRAL_API_KEY`**: Required if `ACTIVE_LLM="mistral"`.
*   **`POSTGRES_URL`**: (Optional) To connect to a PostgreSQL database instead of the local SQLite file.

*(Never commit actual API keys to the repository).*

---

## 13. CORS Configuration

Located in `src/sihbackend/main.py`.
Currently configured for open development access:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
*(Expected to be locked down to the frontend's domain in production).*

---

## 14. Frontend Integration Contract

**TL;DR for Frontend Devs:**
1.  Send `{ "query": "Your formulation text" }` to `POST /api/v1/chat/message`.
2.  Render the `executive_answer`, map over the `evidence` array to show citations, and display `key_findings`/`next_steps`.
3.  Send the exact same `{ "query": "Your formulation text" }` to `POST /api/v1/prior-art/graph`.
4.  Render a node-link diagram mapping the `formulation` node to the returned `evidence` nodes using the provided `edges`.
5.  If `ChatResponse.confidence === 0`, display a banner indicating the AI is degraded but show the raw `evidence` to the user anyway.

---

## 15. Known Limitations / Not Yet Implemented

*   **Database Persistence:** Chat history is not yet being saved to the `UserSession` table.
*   **Authentication:** No user auth/login is implemented.
*   **Advanced Filtering:** Jurisdiction filtering inside the Chroma search query is not yet implemented (it's passed to the LLM, but Chroma currently retrieves globally).
*   **Dynamic Data Ingestion:** No API exists to upload new PDFs; ingestion is strictly via backend CLI scripts.

---

## 16. Example Payloads

### `/api/v1/chat/message`
**Request:**
```json
{
  "query": "Neem extract for treating skin conditions like acne",
  "jurisdiction": "India"
}
```
**Response:**
```json
{
  "executive_answer": "Using Neem extract for skin conditions is heavily documented in TKDL prior art...",
  "confidence": 90,
  "source_agreement": 90,
  "jurisdiction_coverage": 100,
  "evidence_count": 2,
  "applicable_ip_types": ["Trade secret"],
  "key_findings": ["Prior Indian application 1212/DEL/2009 for Neem was abandoned due to Section 3(p)."],
  "next_steps": ["Consult IP attorney regarding non-obvious synergistic effects."],
  "evidence": [
    {
      "id": "ev_pa_0",
      "number": "neem.pdf",
      "jurisdiction": "India",
      "risk": "risk",
      "title": "Prior Art Record for Neem",
      "whyRelevant": "Match (Rerank: 0.97 | L2: 0.63). [Plant: Neem] 1212/DEL/2009: TKDL prior-art..."
    }
  ]
}
```

### `/api/v1/prior-art/graph`
**Request:**
```json
{
  "query": "Neem extract"
}
```
**Response:**
```json
{
  "nodes": [
    {
      "id": "formulation_0",
      "label": "User Formulation",
      "layer": "formulation",
      "passage": "Neem extract"
    },
    {
      "id": "evidence_0",
      "label": "Neem Evidence",
      "layer": "patent",
      "source": "ipindia",
      "jurisdiction": "India",
      "caseNumber": "1212/DEL/2009",
      "verification": "Match (Rerank: 0.97 | L2: 0.63) from neem.pdf",
      "passage": "TKDL prior-art material includes Neem for skin-related conditions..."
    }
  ],
  "edges": [
    ["formulation_0", "evidence_0"]
  ]
}
```

---

## 17. Frontend Assumptions

*   The frontend is expected to handle state synchronization between the Chat view and the Graph view. The backend does not maintain a session-level state tying a chat query to a graph visualization; they are independent, stateless API calls.
*   If the frontend desires the graph to reflect the chat, it must explicitly pass the identical `query` payload to both endpoints simultaneously.
