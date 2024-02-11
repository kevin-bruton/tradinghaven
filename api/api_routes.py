from typing import Annotated
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from api.routers import trades, strategies, ib
from utils.config import get_config_value

openapi_url = '/openapi.json' if get_config_value('enable_openapi_docs') else ''
app = FastAPI(openapi_url=openapi_url)

@app.middleware('http')
async def client_authentication(request: Request, call_next):
    client_id = request.headers.get('ClientId')
    if client_id != get_config_value('client_id'):
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    return await call_next(request)

app.include_router(trades.router)
app.include_router(strategies.router)
app.include_router(ib.router)

@app.get("/hello")
def read_root():
    return {"Hello": "World"}
