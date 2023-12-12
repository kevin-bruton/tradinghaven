import os
from datetime import datetime
from db.orders import get_last_filled_order_id, save_orders, get_order
from db.positions import save_positions
from db.timestamps import get_timestamp, save_timestamp
from utils.config import get_config_value
from utils.telegram import sendMessage

orders = []
positions = []
last_filled_order_id = None
#last_logfile_modification = None
#last_read_log_entry_ts = None

def ts_to_str(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def sendPositionMessage(position):
  enabled = get_config_value('send_position_messages')
  if enabled:
    message = f"""Position change:  
    Strategy: {position['strategy_name']} {position['order_name']}  
    Account: {position['account']}  
    Symbol: {position['symbol']} {position['contract']}  
    Qty: {position['qty']}  
    Price: {position['price']}  
    OPL: {position['opl']}  
    Realized P/L: {position['realized_pl']}   
    Generated: {position['generated']}    
    Final: {position['final']}    
    Action: {position['action']}    
    Order Type: {position['order_type']}    
    State: {position['state']}    
    Fill Qty: {position['fill_qty']}  
    Fill Price: {position['fill_price']}  
    """
    sendMessage(message)

def logtime_to_ts(str):
  return datetime.strptime(str, '%d.%m.%Y/%H:%M:%S.%f').timestamp()

def get_strat_state(state_id):
  if state_id == '2': return 'Transmitted'
  if state_id == '5': return 'Filled'
  return 'unregistered:' + state_id

def get_key_value(content, key):
  key_idx = content.find(key)
  if key_idx == -1:
    return ''
  value_idx = key_idx + len(key) + 1
  value_end_idx = content.find(';', value_idx)
  return content[value_idx:value_end_idx]

def get_strategy_and_order_name(ref):
  parts = ref[2:-1].split(':')
  if len(parts) == 2:
    return parts
  return ['Not_Specified', parts[0]]

def is_strategy_order(content):
  columns = content.split(';')
  return len(columns) > 3 \
    and '@' not in columns[2] \
    and columns[2][:1] == '{'

def process_strategy_order(logentry_ts, content):
  global last_filled_order_id
  columns = content.split(';')
  strategy_name, order_name = get_strategy_and_order_name(columns[2])
  state = get_strat_state(columns[5])
  br_id = int(columns[3])
  br_id_str = columns[14][1:-1]
  found_orders = [o for o in orders if o['br_id'] == br_id]
  if len(found_orders) == 0:
    orders.append({ 'br_id': br_id })
    found_orders = [o for o in orders if o['br_id'] == br_id]
  order = found_orders[0]
  order['strat_state'] = state
  order['br_id_str'] = br_id_str
  order['strategy_name'] = strategy_name
  order['order_name'] = order_name
  order['account'] = columns[15][2:-1]
  order['symbol'] = columns[17][1:-1]
  order['exchange'] = columns[19][1:-1]
  order['contract'] = columns[31][2:-1]
  order['broker_profile'] = columns[47][1:-1]
  order['last_update'] = logentry_ts
  if state == 'Filled':
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
  order['br_id_str'] = get_key_value(content, 'BrIDStr')
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
  order['br_id_str'] = get_key_value(content, 'BrIDStr')
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
    raise Exception('No filled order found')
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
  #if order['state'] == 'Filled':
  positions.append(order)
  sendPositionMessage(order)

def get_logfilepath_modified():
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
    # print('Log file not modified since last read')
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

def get_latest_orders():
  global last_filled_order_id
  logfile, logfile_modified_ts = get_logfilepath_modified()
  if logfile_not_modified_since_last_read(logfile_modified_ts):
    return

  last_read_log_entry_ts = get_timestamp('last_trading_server_log_read')

  last_filled_order_id = get_last_filled_order_id()
  
  # Read log entries
  print('\nUpdating orders and positions at', datetime.now(), '...')
  with open(logfile, 'r') as f:
    for line in f:
      logentry_ts, content = get_logentry_ts_and_content(line)
      if logentry_ts == None or content == None:
        continue

      if logentry_already_processed(logentry_ts, last_read_log_entry_ts):
        continue

      #print(ts_to_str(logentry_ts)[:16], ts_to_str(last_read_log_entry_ts)[:16])
      if ts_to_str(logentry_ts)[:13] != ts_to_str(last_read_log_entry_ts)[:13]:
        print('  Reading log entries at hour: ', ts_to_str(logentry_ts)[:13])
      if is_strategy_order(content):
        process_strategy_order(logentry_ts, content)
      elif is_onorder_event(content):
        process_onorder_event(logentry_ts, content)
      elif is_popactiveorder_event(content):
        process_popactiveorder_event(logentry_ts, content)
      elif is_set_position(content):
        process_set_position(logentry_ts, content)

      last_read_log_entry_ts = logentry_ts

  save_timestamp(last_read_log_entry_ts, 'last_trading_server_log_read')

  orders_inserted = save_orders(orders)
  positions_inserted = save_positions(positions)
  print('  Finished updating orders and positions at', datetime.now(), '- There were', orders_inserted, 'orders and', positions_inserted, 'positions\n')
