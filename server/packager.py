from uvicorn import run

if __name__ == "__main__":
    run("tradinghaven:app", host="0.0.0.0", port=8000)
