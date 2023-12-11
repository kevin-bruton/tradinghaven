import schedule
import time
from .order_retriever import get_latest_orders
from .connection_status import get_connection_status
from utils.config import get_config_value, freq_str_to_secs

def run_cron():
  get_connection_status()
  get_latest_orders()
  print('Initial synchronisation completed!\n')
  conn_freq = freq_str_to_secs(get_config_value('connection_update_frequency'))
  orders_freq = freq_str_to_secs(get_config_value('orders_update_frequency'))

  print('\nStarting cron jobs...\n  Orders update frequency: ', orders_freq, 'seconds\n  Connection status update frequency: ', conn_freq, 'seconds\n')

  schedule.every(orders_freq).seconds.do(get_latest_orders)
  schedule.every(conn_freq).seconds.do(get_connection_status)

  while True:
    schedule.run_pending()
    time.sleep(1)
