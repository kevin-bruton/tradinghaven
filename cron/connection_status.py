import os
from datetime import datetime
from db.connection_events import save_connection_events
from db.timestamps import get_timestamp, save_timestamp
from utils.config import get_config_value
from utils.telegram import sendMessage

last_ib_tws_status_connected = None
last_tws_mc_status_connected = None
last_data_status_connected = None
connection_events = []

last_logfile_modification = None
last_read_log_entry_ts = None

def ts_to_str(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def logtime_to_ts(str):
  return datetime.strptime(str, '%d.%m.%Y/%H:%M:%S.%f').timestamp()

def sendConnectionMessage(message):
  if get_config_value('send_connection_messages'):
    sendMessage(message)

def is_ib_tws_connected_event(content):
  return bool(content.count('Connectivity between IB and Trader Workstation has been restored'))

def process_ib_tws_connected_event(ts):
  global last_ib_tws_status_connected
  if last_ib_tws_status_connected != True:
    connection_events.append({ 'ts': ts, 'type': 'ib_tws', 'connected': True })
    last_ib_tws_status_connected = True
    sendConnectionMessage(f'{ts_to_str(ts)}: IB - TWS Connection Restored')

def is_ib_tws_disconnected_event(content):
  return bool(content.count('Connectivity between IB and Trader Workstation has been lost'))

def process_ib_tws_disconnected_event(ts):
  global last_ib_tws_status_connected
  if last_ib_tws_status_connected != False:
    connection_events.append({ 'ts': ts, 'type': 'ib_tws', 'connected': False })
    last_ib_tws_status_connected = False
    sendConnectionMessage(f'{ts_to_str(ts)}: IB - TWS Connection Lost')

def is_tws_mc_connected_event(content):
  return bool(content.count('<= ib_server::CIBServerImpl::OnConnectionRestored'))

def process_tws_mc_connected_event(ts):
  global last_tws_mc_status_connected
  if last_tws_mc_status_connected != True:
    connection_events.append({ 'ts': ts, 'type': 'tws_mc', 'connected': True })
    last_tws_mc_status_connected = True
    sendConnectionMessage(f'{ts_to_str(ts)}: TWS - MC Connection Restored')

def is_tws_mc_disconnected_event(content):
  return bool(content.count('<= ib_server::CIBServer::OnConnectionLost')) \
    or bool(content.count('Couldn\'t connect to TWS'))

def process_tws_mc_disconnected_event(ts):
  global last_tws_mc_status_connected
  if last_tws_mc_status_connected != False:
    connection_events.append({ 'ts': ts, 'type': 'tws_mc', 'connected': False })
    last_tws_mc_status_connected = False
    sendConnectionMessage(f'{ts_to_str(ts)}: TWS - MC Connection Lost')

def is_data_connected_event(content):
  return bool(content.count('Market data farm connection is OK:usfuture')) \
    or bool(content.count('All data farms are connected'))

def process_data_connected_event(ts):
  global last_data_status_connected
  if last_data_status_connected != True:
    connection_events.append({ 'ts': ts, 'type': 'data', 'connected': True })
    last_data_status_connected = True
    sendConnectionMessage(f'{ts_to_str(ts)}: Data Connection Restored')

def is_data_disconnected_event(content):
  return bool(content.count('Market data farm connection is broken:usfuture'))

def process_data_disconnected_event(ts):
  global last_data_status_connected
  if last_data_status_connected != False:
    connection_events.append({ 'ts': ts, 'type': 'data', 'connected': False })
    last_data_status_connected = False
    sendMessage(f'{ts_to_str(ts)}: Data Connection Lost')

def get_connection_status():
  global last_logfile_modification
  global last_read_log_entry_ts
  logdir = os.path.join(get_config_value('multicharts_data_directory'), 'Logs/TradingServer/')
  logfiles = [f for f in os.listdir(logdir) if f.startswith('TWSTradingPlugin')]
  if len(logfiles) == 0:
    return

  # Get the latest trading server log file name (as there may be more than one)
  last_modified = 0
  logfile = ''
  for logf in logfiles:
    t_modified = os.path.getmtime(logdir + logf)
    if t_modified > last_modified:
      last_modified = t_modified
      logfile = logf

  # Only start reading the log file if it has been modified since the last read
  if last_logfile_modification == None:
    last_logfile_modification = get_timestamp('last_tws_logfile_modification')
    if last_logfile_modification == None:
      last_logfile_modification = 0
  if last_modified <= last_logfile_modification:
    print('  TWS log file not modified since last read')
    return
  save_timestamp(last_modified, 'last_tws_logfile_modification')
  last_logfile_modification = last_modified

  # Get the last read log entry timestamp
  if last_read_log_entry_ts == None:
    last_read_log_entry_ts = get_timestamp('last_tws_log_read')
  
  # Read log entries
  with open(logdir + logfile, 'r') as f:
  # with open('C:/Users/Admin/repo/trading-haven/cron/TWSTradingPlugin_874C_34636_Trace.txt', 'r') as f:
    for line in f:
      content_idx = line.find(' ')
      if content_idx == -1:
        continue

      # Only process log entries that are after the last read log entry
      line_split = line[:content_idx].split('-')
      if len(line_split) < 3 or len(line_split[2]) != 23:
        #print('Invalid log entry:', line)
        continue
      current_log_entry_timestamp = logtime_to_ts(line_split[2])

      if last_read_log_entry_ts and current_log_entry_timestamp < last_read_log_entry_ts:
        #print('already read this log entry', ts_to_str(last_read_log_entry_ts), ts_to_str(current_log_entry_timestamp))
        continue
        #pass
      #print('New log entry:', ts_to_str(last_read_log_entry_ts), ts_to_str(current_log_entry_timestamp))
      last_read_log_entry_ts = current_log_entry_timestamp
      save_timestamp(last_read_log_entry_ts, 'last_tws_log_read')

      content = line[content_idx+1:].strip()
      if is_ib_tws_connected_event(content):
        process_ib_tws_connected_event(current_log_entry_timestamp)
      if is_tws_mc_connected_event(content):
        process_tws_mc_connected_event(current_log_entry_timestamp)
      if is_data_connected_event(content):
        process_data_connected_event(current_log_entry_timestamp)
      if is_ib_tws_disconnected_event(content):
        process_ib_tws_disconnected_event(current_log_entry_timestamp)
      if is_tws_mc_disconnected_event(content):
        process_tws_mc_disconnected_event(current_log_entry_timestamp)
      if is_data_disconnected_event(content):
        process_data_disconnected_event(current_log_entry_timestamp)

  num_inserted_connection_events = save_connection_events(connection_events)
  print('  Saved', num_inserted_connection_events, 'connection events')
