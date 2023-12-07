from uvicorn import run

def run_api_server():
  print('Starting API server...')
  run("api_routes:app", host="0.0.0.0", port=8000)
