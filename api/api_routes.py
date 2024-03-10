from typing import Annotated
from fastapi import FastAPI, Header, HTTPException, Request, Response, status, responses
from api.routers import trades, strategies, ib, connection
from utils.config import get_config_value

openapi_url = '/openapi.json' if get_config_value('enable_openapi_docs') else ''
app = FastAPI(openapi_url=openapi_url)

# app.mount("/status", staticfiles.StaticFiles(directory='api/static'), name="static")

@app.middleware('http')
async def client_authentication(request: Request, call_next):
    print('request items: ', request.query_params.items(), request.path_params.items(), request.headers.get('referer'))
    #request.
    client_id = request.headers.get('ClientId') or request.query_params.get('ClientId')
    print('Client id: ', client_id)
    if client_id != get_config_value('client_id'):
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return await call_next(request)

app.include_router(trades.router)
app.include_router(strategies.router)
app.include_router(ib.router)
app.include_router(connection.router)

@app.get("/hello")
def read_root():
    return {"Hello": "World"}

@app.get("/status")
def get_status_req() -> str:
    try:
        with open(get_config_value('log_dir') + 'live_status.html', 'r') as f:
            statusHtml = f.read()
        return responses.HTMLResponse(content=statusHtml, status_code=200)
    except Exception as e:
        print('Error reading status file: ', e)
        return 'No status available'
