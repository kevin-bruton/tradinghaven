from fastapi import APIRouter
from db.strategies import get_strategies, get_strategies_accounts

router = APIRouter(prefix='/strategies')

@router.get("/accounts")
async def get_strategies_accounts_req():
    return get_strategies_accounts()

@router.get("/")
async def get_strategies_req():
    return get_strategies()
