from fastapi import APIRouter
from sihbackend.schemas.prior_art import PriorArtGraphRequest, PriorArtGraphResponse
from sihbackend.services.prior_art_service import build_prior_art_graph

router = APIRouter(prefix="/api/v1/prior-art", tags=["Prior Art"])

@router.post("/graph", response_model=PriorArtGraphResponse)
async def prior_art_graph(request: PriorArtGraphRequest):
    return build_prior_art_graph(request.query)
