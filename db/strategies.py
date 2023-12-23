from .common import mutate_many, query_one

def get_strategy_by_trader_id (trader_id):
  sql = 'SELECT * FROM strategies WHERE trader_id = ?'
  values = (trader_id, )
  result = query_one(sql, values)
  if result and len(result):
      strategy = {'el_trader_id': result[0], 'trader_id': trader_id, 'strategy_name': result[2]}
      return strategy
  return None

def get_strategy_by_el_trader_id (el_trader_id):
  sql = 'SELECT el_trader_id, trader_id, strategy_name FROM strategies WHERE el_trader_id = ?'
  values = (el_trader_id, )
  result = query_one(sql, values)
  if result and len(result):
      strategy = {'el_trader_id': result[0], 'strategy_name': result[2]}
      if result[1]:
         strategy['trader_id'] = result[1]
      return strategy
  return None

def save_strategies(strategies):
  with_trader_id_values = [(
      s['el_trader_id'],
      s['trader_id'],
      s['strategy_name']
    ) for s in strategies if 'trader_id' in s]
  without_trader_id_values = [(
      s['el_trader_id'],
      s['strategy_name']
    ) for s in strategies if 'trader_id' not in s]
  
  with_trader_id_sql = '''
      INSERT OR REPLACE INTO strategies
      (el_trader_id, trader_id, strategy_name)
      VALUES (?,?,?)
    '''
  without_trader_id_sql = '''
      INSERT OR REPLACE INTO strategies
      (el_trader_id, strategy_name)
      VALUES (?,?)
    '''
  try:
    with_trader_id_inserted = mutate_many(with_trader_id_sql, with_trader_id_values)
    without_trader_id_inserted = mutate_many(without_trader_id_sql, without_trader_id_values)
    return with_trader_id_inserted + without_trader_id_inserted
  except Exception as e:
    print('Error trying to save strategies:')
    for strategy in strategies:
      print(strategy)
  return False
