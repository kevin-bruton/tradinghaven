from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_method():
    return {"ping": "pong2"}
