from uvicorn import run
from utils.config import get_config_value

def run_api_server():
  print('Starting API server...')
  run("api_routes:app", \
      host="0.0.0.0", \
      port=443, \
      ssl_keyfile=get_config_value('ssl_privkey'), \
      ssl_certfile=get_config_value('ssl_fullchain')
    )
