from time import sleep
from fastapi import APIRouter
from api.ib_requests import set_req, get_res

router = APIRouter(prefix='/ib')
timeout = 5

@router.get("/accounts")
async def get_accounts_req():
    set_req({ 'name': 'accounts'})
    resp = None
    timecount = 0
    while resp == None or timecount > timeout:
        resp = get_res('accounts')
        sleep(1)
        timecount += 1
    print('accounts response:', resp)
    return resp

# Get a day of 1min bars
@router.get("/data/{symbol}/{day_YYYYMMDD}")
async def get_data_req(symbol: str, day_YYYYMMDD: str):
    set_req({ 'name': 'data', 'symbol': symbol, 'day_YYYYMMDD': day_YYYYMMDD})
    resp = None
    timecount = 0
    while resp == None or timecount > timeout:
        resp = get_res('data')
        sleep(1)
        timecount += 1
    #print('data response:', resp)
    return resp