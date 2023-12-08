from datetime import datetime
from .common import mutate_many

def str_to_ts(str):
  return datetime.strptime(str, '%Y-%m-%d %H:%M:%S.%f').timestamp()
def ts_to_str(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def save_connection_events(connection_events: list[dict]):
  values = [(
      f"{ts_to_str(c['ts'])}_{c['type']}",
      ts_to_str(c['ts']),
      c['type'],
      c['connected']
    ) for c in connection_events]
  sql = '''
    INSERT OR IGNORE INTO connection_events
      (id, ts, type, connected)
      VALUES(?,?,?,?)
  '''
  return mutate_many(sql, values)
