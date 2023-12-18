from .common import mutate_many, query_one

def get_strategy (trader_id):
  sql = 'SELECT * FROM strategies WHERE trader_id = ?'
  values = (trader_id, )
  result = query_one(sql, values)
  if result and len(result):
      return result[0]
  return None

def save_strategies(strategies):
  sql = '''
      INSERT OR REPLACE INTO strategies
      (el_trader_id, trader_id, strategy_name)
      VALUES (?,?,?)
    '''
  values = [(
    s['el_trader_id'],
    s['trader_id'],
    s['strategy_name']
  ) for s in strategies]
  try:
    return mutate_many(sql, values)
  except Exception as e:
    print('Error trying to save orders:')
    for strategy in strategies:
      print(strategy)
  return False
