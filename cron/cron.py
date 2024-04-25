import schedule
import time
#from .order_retriever import get_latest_orders, get_all_orders
# from .connection_status_log import get_connection_status
from cron.trading_status import processTradingStatus
from utils.config import get_config_value, freq_str_to_secs

def run_cron():
  enable_cron = get_config_value('enable_cron')
  
  # get_connection_status()
  # get_all_orders()
  print('Initial synchronisation completed!\n')
  
  if not enable_cron:
    return
  
  conn_freq = freq_str_to_secs(get_config_value('connection_update_frequency'))
  # orders_freq = freq_str_to_secs(get_config_value('orders_update_frequency'))

  print('\nStarting cron jobs...\n')#  Orders update frequency: ', orders_freq, 'seconds\n  Connection status update frequency: ', conn_freq, 'seconds\n')

  # Instead of scheduling the recollection of order information:
  # the new approach it to get all info at startup and then only when an execution is caught from IB
  # schedule.every(orders_freq).seconds.do(get_latest_orders)
  schedule.every(conn_freq).seconds.do(processTradingStatus)

  while True:
    schedule.run_pending()
    time.sleep(1)
