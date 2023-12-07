print('\n#####################################################')
print('                TRADING HAVEN SERVER                 ')
print('#####################################################\n')

from os import path

root_dir = path.abspath(path.dirname(__file__))
from utils.config import load_config
load_config(root_dir)

from threading import Thread
from cron.cron import run_cron
from api_server import run_api_server
from db.common import init_db

init_db()

cron_thread = Thread(target=run_cron, daemon=True)
api_server_thread = Thread(target=run_api_server, daemon=True)

cron_thread.start()
api_server_thread.start()

try:
    while cron_thread.is_alive() or api_server_thread.is_alive():
        cron_thread.join(1)
        api_server_thread.join(1)
except KeyboardInterrupt:
    print('\n\nCaught KeyboardInterrupt Signal')
    print('Threads joined')
finally:
    print('Server stopped')
    exit(0)
