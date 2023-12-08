import os
from datetime import datetime
from db.orders import save_orders
from db.positions import save_positions
from db.timestamps import get_timestamp, save_timestamp
from utils.config import get_config_value
from utils.telegram import sendMessage

orders = []
positions = []
last_filled_order = None
last_logfile_modification = None
last_read_log_entry_ts = None

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
  return ref[2:-1].split('_')

def is_strategy_order(content):
  columns = content.split(';')
  return len(columns) > 3 \
    and '@' not in columns[2] \
    and columns[2][:1] == '{'

def process_strategy_order(content):
  global last_filled_order
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
  if state == 'Filled':
    last_filled_order = br_id
  
def is_onorder_event(content):
  columns = content.split(' ')
  return len(columns) > 0 \
    and columns[0] == 'CProfile::OnOrder'

def process_onorder_event(content):
  global last_filled_order
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
  if order['state'] == 'Filled':
    last_filled_order = br_id

def is_popactiveorder_event(content):
  columns = content.split(' ')
  return len(columns) > 0 \
    and columns[0] == 'CPositionMonitor::PopActiveOrder'

def process_popactiveorder_event(content):
  global last_filled_order
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
  if order['state'] == 'Filled':
    last_filled_order = br_id
  
def is_set_position(content):
  columns = content.split(' ')
  return len(columns) > 0 and columns[0] == 'CPositionMonitor::SetPosition'

def process_set_position(content):
  global last_filled_order
  if last_filled_order == None:
    raise Exception('No filled order found')
  columns = content.split(' ')
  found_orders = [o for o in orders if o['br_id'] == last_filled_order]
  if len(found_orders) == 0:
    orders.append({ 'br_id': last_filled_order })
    found_orders = [o for o in orders if o['br_id'] == last_filled_order]
  order = found_orders[0]
  order['opl'] = float(columns[6].split('=')[1][:-1])
  order['opl_orig'] = float(columns[7].split('=')[1][:-1])
  order['realized_pl'] = float(columns[8].split('=')[1][:-1])
  positions.append(order)
  sendPositionMessage(order)

def save_orders_table():
  with open('orders.csv', 'w') as f:
    f.write('br_id,br_id_str,strategy_name,order_name,account,symbol,exchange,contract,broker_profile,strat_state,opl,realized_pl,generated,final,action,order_type,qty,price,state,fill_qty,fill_price\n')
    for order in orders:
      f.write(str(order.get('br_id', '')) + ',')
      f.write(order.get('br_id_str', '') + ',')
      f.write(order.get('strategy_name', '') + ',')
      f.write(order.get('order_name', '') + ',')
      f.write(order.get('account', '') + ',')
      f.write(order.get('symbol', '') + ',')
      f.write(order.get('exchange', '') + ',')
      f.write(order.get('contract', '') + ',')
      f.write(order.get('broker_profile', '') + ',')
      f.write(order.get('strat_state', '') + ',')
      f.write(str(order.get('opl', '')) + ',')
      f.write(str(order.get('realized_pl', '')) + ',')
      f.write(order.get('generated', '') + ',')
      f.write(order.get('final', '') + ',')
      f.write(order.get('action', '') + ',')
      f.write(order.get('order_type', '') + ',')
      f.write(str(order.get('qty', '')) + ',')
      f.write(str(order.get('price', '')) + ',')
      f.write(order.get('state', '') + ',')
      f.write(str(order.get('fill_qty', '')) + ',')
      f.write(str(order.get('fill_price', '')) + '\n')

def save_positions_table():
  with open('positions.csv', 'w') as f:
    f.write('br_id,br_id_str,strategy_name,order_name,account,symbol,exchange,contract,broker_profile,strat_state,opl,realized_pl,generated,final,action,order_type,qty,price,state,fill_qty,fill_price\n')
    for positions in positions:
      f.write(str(positions.get('br_id', '')) + ',')
      f.write(positions.get('br_id_str', '') + ',')
      f.write(positions.get('strategy_name', '') + ',')
      f.write(positions.get('order_name', '') + ',')
      f.write(positions.get('account', '') + ',')
      f.write(positions.get('symbol', '') + ',')
      f.write(positions.get('exchange', '') + ',')
      f.write(positions.get('contract', '') + ',')
      f.write(positions.get('broker_profile', '') + ',')
      f.write(positions.get('strat_state', '') + ',')
      f.write(str(positions.get('opl', '')) + ',')
      f.write(str(positions.get('realized_pl', '')) + ',')
      f.write(positions.get('generated', '') + ',')
      f.write(positions.get('final', '') + ',')
      f.write(positions.get('action', '') + ',')
      f.write(positions.get('order_type', '') + ',')
      f.write(str(positions.get('qty', '')) + ',')
      f.write(str(positions.get('price', '')) + ',')
      f.write(positions.get('state', '') + ',')
      f.write(str(positions.get('fill_qty', '')) + ',')
      f.write(str(positions.get('fill_price', '')) + '\n')

def get_latest_orders():
  global last_logfile_modification
  global last_read_log_entry_ts
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

  # Only start reading the log file if it has been modified since the last read
  if last_logfile_modification == None:
    last_logfile_modification = get_timestamp('last_trading_server_logfile_modification')
    if last_logfile_modification == None:
      last_logfile_modification = 0
  if last_modified <= last_logfile_modification:
    # print('Log file not modified since last read')
    return
  save_timestamp(last_modified, 'last_trading_server_logfile_modification')
  last_logfile_modification = last_modified

  # Get the last read log entry timestamp
  if last_read_log_entry_ts == None:
    last_read_log_entry_ts = get_timestamp('last_trading_server_log_read')
  
  # Read log entries
  with open(logdir + logfile, 'r') as f:
    for line in f:
      content_idx = line.find(' ')
      if content_idx == -1:
        continue

      # Only process log entries that are after the last read log entry
      line_split = line[:content_idx].split('-')
      if len(line_split) >= 3 and len(line_split[2]) == 23: 
        current_log_entry_timestamp = logtime_to_ts(line_split[2])
      else:
        continue

      if last_read_log_entry_ts and current_log_entry_timestamp < last_read_log_entry_ts:
        #print('already read this log entry', last_read_log_entry_ts, current_log_entry_timestamp)
        continue
      #print('New log entry:', last_read_log_entry_ts, current_log_entry_timestamp)
      last_read_log_entry_ts = current_log_entry_timestamp
      save_timestamp(last_read_log_entry_ts, 'last_trading_server_log_read')

      content = line[content_idx+1:].strip()
      if is_strategy_order(content):
        process_strategy_order(content)
      elif is_onorder_event(content):
        process_onorder_event(content)
      elif is_popactiveorder_event(content):
        process_popactiveorder_event(content)
      elif is_set_position(content):
        process_set_position(content)

  # save_orders_table()
  # save_positions_table()
  orders_inserted = save_orders(orders)
  positions_inserted = save_positions(positions)
  print('Saved', orders_inserted, 'orders and', positions_inserted, 'positions')
