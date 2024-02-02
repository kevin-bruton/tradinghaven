from fastapi import APIRouter
from db.strategies import get_strategy_trades

router = APIRouter(prefix='/trades')

@router.get("/{strategyName}/{accountId}")
async def trades_req(strategyName, accountId):
    trades = get_strategy_trades(strategyName, accountId)
    return trades
