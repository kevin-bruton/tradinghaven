import os
from datetime import datetime
from db.orders import get_last_filled_order_id, save_orders, get_order
from db.positions import save_positions
from db.timestamps import get_timestamp, save_timestamp
from utils.config import get_config_value
from utils.telegram import send_message

orders = []
positions = []
last_filled_order_id = None
strategy_ids = []
#last_logfile_modification = None
#last_read_log_entry_ts = None

def ts_to_str(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def sendPositionMessage(position):
  def pos_get(key):
    return position[key] if key in position else 'N/A'
  enabled = get_config_value('send_position_messages')
  if enabled:
    message = f"""Position change:  
    Strategy: {pos_get('strategy_name')}  
    Order name: {pos_get('order_name')}  
    Account: {pos_get('account')}  
    Symbol: {pos_get('symbol')} {pos_get('contract')}  
    Qty: {pos_get('qty')}  
    Price: {pos_get('price')}  
    Generated: {pos_get('generated')}    
    Final: {pos_get('final')}    
    Action: {pos_get('action')}    
    Order Type: {pos_get('order_type')}    
    State: {pos_get('state')}    
    Fill Qty: {pos_get('fill_qty')}  
    Fill Price: {pos_get('fill_price')}  
    OPL: {pos_get('opl')}  
    Realized P/L: {pos_get('realized_pl')}   
    """
    send_message(message)

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

def is_strategy_identifier(content):
  columns = content.split(';')
  return len(columns) > 50 \
    and '@' in columns[2] \
    and columns[2][1] == '{'

def process_strategy_identifier(logentry_ts, content):
  global strategy_ids
  columns = content.split(';')
  trader_id = columns[1]
  strategy_name = columns[44]
  strategy_ids.append([trader_id, strategy_name])

def get_auto_strategy_name(trader_id):
  global strategy_ids
  found = [s[1] for s in strategy_ids if strategy_ids[0] == trader_id]
  if len(found):
    return found[1]
  return 'Not found'

def is_strategy_order(content):
  columns = content.split(';')
  return len(columns) > 50 \
    and '@' not in columns[2] \
    and columns[2][:1] == '{'

def process_strategy_order(logentry_ts, content):
  global last_filled_order_id
  columns = content.split(';')
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
  # order['trader_id'] = int(columns[4])
  order['auto_strat_name'] = get_auto_strategy_name(order['trader_id'])
  order['order_name'] = columns[2][2:-1]
  order['account'] = columns[15][2:-1]
  order['symbol'] = columns[17][1:-1]
  order['exchange'] = columns[19][1:-1]
  order['contract'] = columns[31][2:-1] if len(columns) > 31 else ''
  order['broker_profile'] = columns[47][1:-1]
  order['last_update'] = logentry_ts
  #print('STRAT ORDER')
  #print('  CONTENT:', content)
  #print('  ORDER:', order)
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
  order['trader_id'] = get_key_value(content, 'ELTraderID')
  order['auto_strat_name'] = get_auto_strategy_name(order['trader_id'])
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
  order['trader_id'] = get_key_value(content, 'ELTraderID')
  order['auto_strat_name'] = get_auto_strategy_name(order['trader_id'])
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
    print('  No updates since last check')
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
  try:
    logfile, logfile_modified_ts = get_logfilepath_modified()
  except:
    print('Error: could not read from TradingServer')
    return
  if logfile_not_modified_since_last_read(logfile_modified_ts):
    print('No TradingServer updates since last check')
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

      last_read_log_entry_ts = logentry_ts

  save_timestamp(last_read_log_entry_ts, 'last_trading_server_log_read')

  orders_inserted = save_orders(orders)
  positions_inserted = save_positions(positions)
  print('  Finished updating orders and positions at', datetime.now(), '- There were', orders_inserted, 'orders and', positions_inserted, 'positions\n')
