from datetime import datetime
from .common import mutate_one, query_one

def str_to_ts(str):
  return datetime.strptime(str, '%Y-%m-%d %H:%M:%S.%f').timestamp()
def ts_to_str(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def save_timestamp(timestamp: float, type: str):
  ts_str = ts_to_str(timestamp)
  #print('Saving timestamp to db: ', timestamp, ' for type: ', type)

  sql = '''
    INSERT OR REPLACE INTO timestamps
      (timestamp, type)
    VALUES(?,?)
  '''
  return mutate_one(sql, (ts_str, type))

def get_timestamp(type: str) -> float:
  sql = '''
    SELECT timestamp FROM timestamps WHERE type = ? ORDER BY timestamp DESC LIMIT 1
  '''
  result = query_one(sql, (type,))
  if result == None: return 0
  if len(result) == 0: return 0
  return str_to_ts(result[0])