import json
from os import path

default_config = {
  "database_directory": ".",
  "multicharts_data_directory": ".",
  "orders_update_frequency": "1_h",
  "connection_update_frequency": "15_s",
  "send_connection_messages": False,
  "send_position_messages": False,
  "telegram_token": "",
  "telegram_chat_id": ""
}

def load_config(root_dir):
  global config
  config_file = path.join(root_dir, 'config.json')
  if not path.exists(config_file):
    with open(config_file, "w") as file:
      json.dump(default_config, file, indent=2)
    config = default_config
  else:
    with open(config_file, "r") as file:
      config = json.load(file)
  config['root_dir'] = root_dir

def get_config_value(key):
  return config[key]

def freq_str_to_secs(freq):
  freq, units = freq.split('_')
  if units == 's': return int(freq)
  elif units == 'm': return int(freq) * 60
  elif units == 'h': return int(freq) * 60 * 60
  else: raise Exception('Invalid units for update frequency')
