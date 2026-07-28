from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    # simple liveness check, no DB call here on purpose
    return {"status": "ok"}
