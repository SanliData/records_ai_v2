from fastapi import APIRouter
from backend.services.upap.process.text_normalizer import TextNormalizer
from backend.services.upap.process.fuzzy_matcher import FuzzyMatcher

router = APIRouter()

@router.post("/search")
def search_archive(query: str):
    # Basit örnek: arsiv kayitlarini bir listeden okuyoruz (gerçek sistemde DB olacak)
    records = ["pink floyd the wall", "beatles abbey road", "nirvana nevermind", "radiohead ok computer"]
    query_clean = TextNormalizer.clean(query)
    results = FuzzyMatcher.match(query_clean, records)
    return {"query": query, "results": results}
