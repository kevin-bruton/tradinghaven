print('\n#####################################################')
print('                TRADING HAVEN SERVER                 ')
print('#####################################################\n')

from os import path

root_dir = path.abspath(path.dirname(__file__))
from utils.config import load_config
load_config(root_dir)

from time import sleep
from threading import Thread
from cron.cron import run_cron
from api_server import run_api_server
from db.common import init_db

init_db()

cron_thread = Thread(target=run_cron, daemon=True)
api_server_thread = Thread(target=run_api_server, daemon=True)

api_server_thread.start()
sleep(1)
cron_thread.start()

try:
    while cron_thread.is_alive() or api_server_thread.is_alive():
        cron_thread.join(1)
        api_server_thread.join(1)
finally:
    print('\n\nThe Trading Haven Server has stopped!\n')
    exit(0)
