from fastapi import FastAPI
from routers import positions
from utils.config import get_config_value

openapi_url = '/openapi.json' if get_config_value('enable_openapi_docs') else ''
app = FastAPI(openapi_url=openapi_url)
app.include_router(positions.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
