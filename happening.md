# Implementation Plan: SIH Backend Integration

This document outlines the granular steps to implement the backend features and bridge them to the currently static frontend prototype.

## Phase 1: API Scaffolding, Schemas & Relational DB Foundation
*Goal: Build the backend endpoints to exactly match the frontend's expected data structures, and establish the relational DB for non-semantic data.*

*   [ ] **Step 1: Relational Database Setup**
    *   Initialize the relational database layer (e.g., SQLAlchemy with SQLite/PostgreSQL) for non-semantic data identified in the frontend audit:
        *   `History`: To persist user sessions and reports (`historyService.ts`).
        *   `ReferenceData`: To store `plants`, `sources`, and `jurisdictions` so they can be updated dynamically rather than hardcoded in the frontend.
*   [ ] **Step 2: Define Frontend-Aligned Schemas**
    *   Create Pydantic schemas for `/api/v1/prior-art/graph` matching the frontend's `EvidenceNode` and `[string, string]` edge tuple arrays.
    *   Create Pydantic schemas for `/api/v1/chat/message` to return the fields needed by `assistant.tsx` (executive answer, key findings array, ip types, confidence score, and evidence citations).
*   [ ] **Step 3: Create Mock API Endpoints**
    *   Create `src/sihbackend/api/prior_art.py` and `src/sihbackend/api/chat.py`.
    *   Temporarily return static data that mimics `referenceData.ts` so the frontend can swap its `setTimeout` mocks for real network calls immediately.
*   [ ] **Step 4: Provide Frontend Integration Snippets**
    *   Provide the exact `fetch()` code needed for `assistant.tsx` and `priorArtService.ts`.

## Phase 2: Prior Art Data Ingestion (Semantic Prep)
*Goal: Process the botanical family PDFs into a queryable ChromaDB collection.*

*   [ ] **Step 5: Build Ingestion Script**
    *   Create `scripts/ingest_prior_art.py` targeting `~/Desktop/toChunk/today/family/`.
*   [ ] **Step 6: Implement Custom Chunking & Metadata**
    *   Implement regex chunking (one chunk = one patent/record).
    *   Inject `{"plant_family": "<extracted_name>", "doc_type": "prior_art"}` into metadata.
*   [ ] **Step 7: Execute Ingestion**
    *   Populate the `vectorstore/prior_art` ChromaDB collection.

## Phase 3: Semantic Search Integration (The RAG Core)
*Goal: Replace Phase 1 mocks with real vector search.*

*   [ ] **Step 8: Prior Art Graph Logic**
    *   Update `/api/v1/prior-art/graph`. *(Note: Since the frontend currently has no query state passed to `/prior-art`, this endpoint will initially use a default formulation query, perform a vector search on `vectorstore/prior_art`, and dynamically format the chunks into the graph nodes/edges).*
*   [ ] **Step 9: AI Assistant Legal/Prior-Art RAG**
    *   Update `/api/v1/chat/message` to take the user's string input.
    *   Query the existing `vectorstore/legal` (and optionally `prior_art`) to generate a grounded IP assessment using LangChain.

## Phase 4: Refinement
*Goal: Improve accuracy of patent retrieval.*

*   [ ] **Step 10: Implement Reranking**
    *   Integrate a cross-encoder to re-rank the top 15 results from ChromaDB, filtering out false positives caused by dense patent terminology.
