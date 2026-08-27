from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Health check")
async def health_check() -> dict:
    """
    Returns service health status.
    Used by load balancers and monitoring systems.
    """
    return {"status": "ok"}
