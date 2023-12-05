from os import path
root_dir = path.abspath(path.dirname(__file__) + '/..')
from utils.config import load_config
load_config(root_dir)

from threading import Thread
from cron.cron import run_cron
from api_server import run_api_server
from db.common import init_db

init_db()

cron_thread = Thread(target=run_cron)
api_server_thread = Thread(target=run_api_server)

cron_thread.start()
api_server_thread.start()
