from time import sleep
from fastapi import APIRouter
from api.ib_requests import set_req, get_res

router = APIRouter(prefix='/ib')
timeout = 5

@router.get("/accounts")
async def get_accounts_req():
    set_req('accounts')
    resp = None
    timecount = 0
    while resp == None or timecount > timeout:
        resp = get_res('accounts')
        sleep(1)
        timecount += 1
    print('accounts response:', resp)
    return resp
