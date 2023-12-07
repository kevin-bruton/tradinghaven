from fastapi import FastAPI
from routers import positions

app = FastAPI()
app.include_router(positions.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
