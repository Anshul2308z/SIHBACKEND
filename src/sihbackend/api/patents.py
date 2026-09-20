from fastapi import APIRouter
from typing import List
import hashlib
from sihbackend.schemas.patents import PatentSearchRequest, PatentRecord
from sihbackend.services.chat_service import _get_vectorstores

router = APIRouter(prefix="/api/v1/patents", tags=["Patents"])

@router.post("/search", response_model=List[PatentRecord])
def search_patents(request: PatentSearchRequest):
    pa_store, _ = _get_vectorstores()
    
    if not pa_store:
        return []

    # Prepare filter
    where_filter = {}
    if request.scope == "India":
        where_filter["jurisdiction"] = "India"
    elif request.scope == "International":
        where_filter["jurisdiction"] = {"$ne": "India"} # Basic approximation
        
    if request.plant != "All" and request.plant != "All plants":
        # we can't easily multi-filter in simple chroma dict without $and, so let's filter in python for now
        pass 

    results = pa_store.similarity_search_with_score(request.query, k=15, filter=where_filter if where_filter else None)
    
    records = []
    seen_sources = set()
    
    for doc, dist in results:
        source = doc.metadata.get("source", "Unknown")
        # Deduplicate identical sources so we get diverse results
        if source in seen_sources:
            continue
        seen_sources.add(source)
        
        # Calculate percentage similarity from L2 distance (typically 0.0 to 2.0 in normalized embeddings)
        # 0.0 = 100%, 1.0 = ~50%
        similarity = int(max(0, (1 - (dist / 2.0)) * 100))
        
        # Determine status/risk dynamically
        risk = "risk" if similarity > 80 else "review" if similarity > 60 else "verified"
        
        plant = doc.metadata.get("plant_family", "Unknown Plant")
        jurisdiction = doc.metadata.get("jurisdiction", "India")
        j_group = "India" if jurisdiction == "India" else "International"
        
        # Python-side filtering for plants
        if request.plant not in ["All", "All plants"] and request.plant.lower() != plant.lower():
            continue
            
        rec = PatentRecord(
            id=hashlib.md5(f"{source}_{plant}".encode()).hexdigest()[:8],
            number=f"REC-{source.split('.')[0].upper()[:6]}-{hashlib.md5(source.encode()).hexdigest()[:4]}",
            title=f"Patent / Prior Art Record for {plant}",
            applicant="Official Database Record",
            jurisdiction=jurisdiction,
            jurisdictionGroup=j_group,
            published="2023-01-01", # Mocked
            similarity=similarity,
            status="Published",
            risk=risk,
            whyRelevant=doc.page_content[:150] + "...",
            concepts=[plant, "Traditional Knowledge"],
            sources=["TKDL" if "tkdl" in source.lower() else "WIPO"],
            plants=[plant],
            family="Unknown",
            indication="Various",
            ipType="Patent",
            evidenceLevel="Official record"
        )
        records.append(rec)
        
        if len(records) >= 8:
            break
            
    return records
