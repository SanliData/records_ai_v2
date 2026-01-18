from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def placeholder():
    return {"status": "not_implemented"}
