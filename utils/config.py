import json
import yaml
from os import path

config = {}

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
  config_file = path.join(root_dir, 'config.yaml')
  if not path.exists(config_file):
    with open(config_file, "w") as file:
      #json.dump(default_config, file, indent=2)
      yaml.dump(default_config, file)
    config = default_config
  else:
    with open(config_file, "r") as file:
      #config = json.load(file)
      config = yaml.safe_load(file)
  config['root_dir'] = root_dir
  print('\nLoaded config:')
  #print(json.dumps(config, indent=2) + '\n')
  print(yaml.dump(config))

def get_config_value(key):
  global config
  if key in config:
    return config[key]
  elif key == 'enable_openapi_docs':
    return False
  elif key == 'enable_api':
    return False
  elif key == 'enable_cron':
    return False
  elif key == 'dev_logfiles':
    return False
  return default_config[key]

def freq_str_to_secs(freq):
  freq, units = freq.split('_')
  if units == 's': return int(freq)
  elif units == 'm': return int(freq) * 60
  elif units == 'h': return int(freq) * 60 * 60
  else: raise Exception('Invalid units for update frequency')
