import os
from zipfile import ZipFile
from datetime import datetime
from db.orders import get_last_filled_order_id, save_log_orders, get_order
from db.positions import save_positions
from db.strategies import save_strategies, \
  get_strategy_by_el_trader_id as db_get_strategy_by_el_trader_id
  # get_strategy_by_trader_id as db_get_strategy_by_trader_id, \
from db.timestamps import get_timestamp, save_timestamp
from utils.config import get_config_value
from utils.telegram import send_position_message

strategies = []
orders = []
positions = []
last_filled_order_id = None

def ts_to_str(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def logtime_to_ts(str):
  return datetime.strptime(str, '%d.%m.%Y/%H:%M:%S.%f').timestamp()

def get_key_value(content, key):
  key_idx = content.find(key)
  if key_idx == -1:
    return ''
  value_idx = key_idx + len(key) + 1
  value_end_idx = content.find(';', value_idx)
  return content[value_idx:value_end_idx]

def is_strategy_identifier(content):
  columns = content.split(';')
  return len(columns) > 50 \
    and '@' in columns[2]

def process_strategy_identifier(logentry_ts, content):
  global strategies
  columns = content.split(';')
  el_trader_id = columns[1]
  strategy_name = columns[44][1:-1]
  strategies.append({'strategy_name': strategy_name, 'el_trader_id': el_trader_id})

def add_strategy_trader_id(el_trader_id, trader_id):
  global strategies
  found = [s for s in strategies if s['el_trader_id'] == el_trader_id]
  if len(found):
    found[0]['trader_id'] = trader_id
    return found[0]
  else:
    strategy = db_get_strategy_by_el_trader_id(el_trader_id)
    if strategy:
      strategy['trader_id'] = trader_id
      strategies.append(strategy)
    return strategy
'''
def get_strategy_by_trader_id(trader_id):
  global strategies
  found = [s for s in strategies if 'trader_id' in s and s['trader_id'] == trader_id]
  if len(found):
    return found[0]
  strategy = db_get_strategy_by_trader_id(trader_id)
  if strategy and 'el_trader_id' in strategy:
    add_strategy_trader_id(strategy['el_trader_id'], trader_id)
  return strategy
'''

def get_strategy_by_el_trader_id(el_trader_id):
  global strategies
  found = [s for s in strategies if 'el_trader_id' in s and s['el_trader_id'] == el_trader_id]
  if len(found):
    return found[0]
  strategy = db_get_strategy_by_el_trader_id(el_trader_id)
  return strategy

def is_strategy_order(content):
  columns = content.split(';')
  return len(columns) > 50 \
    and '@' not in columns[2] \
    and columns[2][:1] == '{'

def process_strategy_order(logentry_ts, content):
  global last_filled_order_id
  columns = content.split(';')
  br_id = int(columns[3])
  br_id_str = columns[14][1:-1]
  found_orders = [o for o in orders if o['br_id'] == br_id]
  if len(found_orders) == 0:
    orders.append({ 'br_id': br_id })
    found_orders = [o for o in orders if o['br_id'] == br_id]
  order = found_orders[0]
  order['br_id_str'] = br_id_str
  order['order_name'] = columns[2][2:-1]
  order['account'] = columns[15][2:-1]
  order['symbol'] = columns[17][1:-1]
  order['exchange'] = columns[19][1:-1]
  order['contract'] = columns[31][2:-1] if len(columns) > 31 else ''
  order['broker_profile'] = columns[47][1:-1]
  order['last_update'] = logentry_ts
  order['cur_price'] = columns[11]
  is_order_filled = columns[5] == '5'
  if is_order_filled:
    last_filled_order_id = br_id
  
def is_onorder_event(content):
  columns = content.split(' ')
  return len(columns) > 0 \
    and columns[0] == 'CProfile::OnOrder'

def process_onorder_event(logentry_ts, content):
  global last_filled_order_id
  columns = content.split(';')
  br_id = int(columns[3].split('=')[1])
  found_orders = [o for o in orders if o['br_id'] == br_id]
  if len(found_orders) == 0:
    orders.append({ 'br_id': br_id })
    found_orders = [o for o in orders if o['br_id'] == br_id]
  order = found_orders[0]
  el_trader_id = get_key_value(content, 'ELTraderID')
  trader_id = get_key_value(content, 'TraderID')
  strategy = add_strategy_trader_id(el_trader_id, trader_id)
  order['br_id_str'] = get_key_value(content, 'BrIDStr')
  order['el_trader_id'] = el_trader_id
  order['trader_id'] = trader_id
  order['strategy_name'] = strategy and 'strategy_name' in strategy and strategy['strategy_name'] \
    or 'strategy_name' in order and order['strategy_name'] or 'Not Found'
  order['generated'] = get_key_value(content, 'Gen')
  order['final'] = get_key_value(content, 'Final')
  order['action'] = get_key_value(content, 'Actn')
  order['order_type'] = get_key_value(content, 'Cat')
  order['qty'] = int(get_key_value(content, 'Qty'))
  order['price'] = float(get_key_value(content, 'Price'))
  order['state'] = get_key_value(content, 'State')
  order['fill_qty'] = int(get_key_value(content, 'FillQty'))
  order['fill_price'] = float(get_key_value(content, 'FillPrice'))
  order['last_update'] = logentry_ts
  if order['state'] == 'Filled':
    last_filled_order_id = br_id

def is_popactiveorder_event(content):
  columns = content.split(' ')
  return len(columns) > 0 \
    and columns[0] == 'CPositionMonitor::PopActiveOrder'

def process_popactiveorder_event(logentry_ts, content):
  global last_filled_order_id
  columns = content.split(';')
  br_id = int(columns[3].split('=')[1])
  found_orders = [o for o in orders if o['br_id'] == br_id]
  if len(found_orders) == 0:
    orders.append({ 'br_id': br_id })
    found_orders = [o for o in orders if o['br_id'] == br_id]
  order = found_orders[0]
  el_trader_id = get_key_value(content, 'ELTraderID')
  trader_id = get_key_value(content, 'TraderID')
  strategy = add_strategy_trader_id(el_trader_id, trader_id)
  order['br_id_str'] = get_key_value(content, 'BrIDStr')
  order['el_trader_id'] = el_trader_id
  order['trader_id'] = trader_id
  order['strategy_name'] = strategy and 'strategy_name' in strategy and strategy['strategy_name'] \
    or 'strategy_name' in order and order['strategy_name'] or 'Not Found'
  order['generated'] = get_key_value(content, 'Gen')
  order['final'] = get_key_value(content, 'Final')
  order['action'] = get_key_value(content, 'Actn')
  order['order_type'] = get_key_value(content, 'Cat')
  order['qty'] = int(get_key_value(content, 'Qty'))
  order['price'] = float(get_key_value(content, 'Price'))
  order['state'] = get_key_value(content, 'State')
  order['fill_qty'] = int(get_key_value(content, 'FillQty'))
  order['fill_price'] = float(get_key_value(content, 'FillPrice'))
  order['last_update'] = logentry_ts
  if order['state'] == 'Filled':
    last_filled_order_id = br_id
  
def is_set_position(content):
  columns = content.split(' ')
  return len(columns) > 0 and columns[0] == 'CPositionMonitor::SetPosition'

def process_set_position(logentry_ts, content):
  global last_filled_order_id
  if last_filled_order_id == None:
    print('No last filled order id. Can\'t associate this position with an order:', content)
    return
  columns = content.split(' ')
  found_orders = [o for o in orders if o['br_id'] == last_filled_order_id]
  if len(found_orders) == 0:
    orders.append({ 'br_id': last_filled_order_id })
    found_orders = [o for o in orders if o['br_id'] == last_filled_order_id]
  order = found_orders[0]
  order['opl'] = float(columns[6].split('=')[1][:-1])
  order['opl_orig'] = float(columns[7].split('=')[1][:-1])
  order['realized_pl'] = float(columns[8].split('=')[1][:-1])
  order['last_update'] = logentry_ts
  positions.append(order)
  if order['realized_pl'] > 0:
    send_position_message(order)

def get_all_logfile_names():
  logdir = os.path.join(get_config_value('multicharts_data_directory'), 'Logs/TradingServer/')
  logfiles = [f for f in os.listdir(logdir) if f.startswith('TradingServer')]
  def logfiles_order(file):
    return os.path.getmtime(logdir + file)
  logfiles.sort(key=logfiles_order)
  return [logdir + f for f in logfiles]

def get_logfilepath_modified():
  dev_logfiles = get_config_value('dev_logfiles')
  if dev_logfiles:
    logdir = os.path.join(get_config_value('root_dir'), 'cron/')
    logfiles = ['TradingServer_2C28_11304_Trace0.txt']
  else:
    logdir = os.path.join(get_config_value('multicharts_data_directory'), 'Logs/TradingServer/')
    logfiles = [f for f in os.listdir(logdir) if f.startswith('TradingServer')]
  if len(logfiles) == 0:
    return
  last_modified = 0
  
  # Get the latest trading server log file name (as there may be more than one)
  logfile = ''
  for logf in logfiles:
    t_modified = os.path.getmtime(logdir + logf)
    if t_modified > last_modified:
      last_modified = t_modified
      logfile = logf
  return [logdir + logfile, last_modified]

def logfile_not_modified_since_last_read(logfile_modified_ts):
  last_read = get_timestamp('last_trading_server_logfile_modification')
  if last_read == None:
    last_read = 0
  if last_read == logfile_modified_ts:
    print('TradingServer logfile has not been modified since last chec. Last:', last_read, '\n')
    return True
  save_timestamp(logfile_modified_ts, 'last_trading_server_logfile_modification')
  return False

def logentry_already_processed(logentry_ts, last_read_log_entry_ts):
  return last_read_log_entry_ts and logentry_ts < last_read_log_entry_ts

def get_logentry_ts_and_content(line):
  content_idx = line.find(' ')
  if content_idx == -1:
    return [None, None]
  line_split = line[:content_idx].split('-')
  if len(line_split) >= 3 and len(line_split[2]) == 23: 
    content = line[content_idx+1:].strip()
    log_ts = logtime_to_ts(line_split[2])
    return [log_ts, content]
  return [None, None]

def get_all_orders():
  last_entry_ts = 0
  logfilepaths = get_all_logfile_names()
  for logfilepath in logfilepaths:
    print('Processing', logfilepath)
    extension = logfilepath.split('.')[-1]
    if extension == 'zip':
      with ZipFile(logfilepath) as zipfile:
        namelist = zipfile.namelist()
        with zipfile.open(namelist[0], 'r') as f:
          for line in f:
            last_entry_ts = process_logentry(line.decode('utf-8'), last_entry_ts)
    else:
      with open(logfilepath, 'r') as f:
        for line in f:
          last_entry_ts = process_logentry(line, last_entry_ts)

  save_timestamp(last_entry_ts, 'last_trading_server_log_read')
  strategies_inserted = save_strategies(strategies)
  orders_inserted = save_log_orders(orders)
  positions_inserted = save_positions(positions)
  print('  Finished processing Trading Server logs at', datetime.now())
  print('     Inserted/updated', strategies_inserted, 'strategies,', orders_inserted, 'orders and', positions_inserted, 'positions\n')
        

def get_latest_orders():
  try:
    logfile, logfile_modified_ts = get_logfilepath_modified()
  except Exception as e:
    print('Error: could not read TradingServer log', e, '\n')
    return
  if logfile_not_modified_since_last_read(logfile_modified_ts):
    return
  
  with open(logfile, 'r') as f:
    #global last_filled_order_id
    last_read_log_entry_ts = get_timestamp('last_trading_server_log_read')
    #last_filled_order_id = get_last_filled_order_id()

    # Read log entries
    print('\nUpdating orders and positions at', datetime.now(), '...')
    for line in logfile:
      last_read_log_entry_ts = process_logentry(line, last_read_log_entry_ts)

    save_timestamp(last_read_log_entry_ts, 'last_trading_server_log_read')
    strategies_inserted = save_strategies(strategies)
    orders_inserted = save_log_orders(orders)
    positions_inserted = save_positions(positions)
    print('  Finished processing Trading Server logs at', datetime.now())
    print('     Inserted/updated', strategies_inserted, 'strategies,', orders_inserted, 'orders and', positions_inserted, 'positions\n')

def process_logentry(line, last_read_log_entry_ts=0):
  logentry_ts, content = get_logentry_ts_and_content(line)
  if logentry_ts == None or content == None:
    return

  if logentry_already_processed(logentry_ts, last_read_log_entry_ts):
    return

  #print(ts_to_str(logentry_ts)[:16], ts_to_str(last_read_log_entry_ts)[:16])
  if last_read_log_entry_ts and ts_to_str(logentry_ts)[:13] != ts_to_str(last_read_log_entry_ts)[:13]:
    print('  Reading log entries at hour: ', ts_to_str(logentry_ts)[:13])
  
  if is_strategy_identifier(content):
    process_strategy_identifier(logentry_ts, content)
  if is_strategy_order(content):
    process_strategy_order(logentry_ts, content)
  elif is_onorder_event(content):
    process_onorder_event(logentry_ts, content)
  elif is_popactiveorder_event(content):
    process_popactiveorder_event(logentry_ts, content)
  elif is_set_position(content):
    process_set_position(logentry_ts, content)

  return logentry_ts

