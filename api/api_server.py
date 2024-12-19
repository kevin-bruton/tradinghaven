from uvicorn import run
from utils.config import get_config_value

def run_api_server():
  print('Starting API server...')
  run("api.api_routes:app", \
      host="localhost", \
      port=10443, \
      #ssl_keyfile=get_config_value('ssl_privkey'), \
      #ssl_certfile=get_config_value('ssl_fullchain')
    )
