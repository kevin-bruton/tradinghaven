from fastapi import APIRouter
from db.strategies import get_strategies

router = APIRouter(prefix='/strategies')

@router.get("/")
async def get_strategies_req():
    return get_strategies()
