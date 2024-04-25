print('\n#####################################################')
print('                TRADING HAVEN SERVER                 ')
print('#####################################################\n')

from os import path
from sys import exit

root_dir = path.abspath(path.dirname(__file__))
from utils.config import load_config, get_config_value
load_config(root_dir)
enable_api = get_config_value('enable_api')

from time import sleep
from threading import Thread
from cron.cron import run_cron
from ib.ib_monitor import run_ib
from api.api_server import run_api_server
from db.common import init_db
from log_analyser.read_logs import read_all_logs

init_db()

if get_config_value('read_logs_on_startup'):
  read_all_logs()

cron_thread = Thread(target=run_cron, daemon=True)
ib_thread = Thread(target=run_ib, daemon=True)
if enable_api:
  api_server_thread = Thread(target=run_api_server, daemon=True)
  api_server_thread.start()
  sleep(5)
cron_thread.start()
ib_thread.start()

try:
  while cron_thread.is_alive() \
    or (enable_api and api_server_thread.is_alive()) \
    or ib_thread.is_alive():
      cron_thread.join(1)
      ib_thread.join(1)
      if enable_api:
        api_server_thread.join(1)
finally:
  print('\n\nThe Trading Haven Server has stopped!\n')
  exit(0)
