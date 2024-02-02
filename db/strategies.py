from .common import mutate_many, query_one, query_many

def get_strategies():
   sql = 'SELECT DISTINCT strategyName, workspace, account, brokerProfile, symbol, symbolRoot, exchange, currency FROM strategies'
   result = query_many(sql)
   return result

def get_strategy_trades(strategyName, accountId):
   sql = '''
      SELECT orders.orderId, orders.symbolRoot, orders.generated, orders.final, orders.execQty, orders.execPrice, orders.orderType, orders.action, orders.stopPrice, orders.limitPrice, orders.commission, orders.realizedPnl
      FROM orders, strategies
      WHERE orders.strategyId = strategies.strategyId
      AND strategies.strategyName = ?
      AND strategies.account = ?
    '''
   result = query_many(sql, (strategyName, accountId))
   return result

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
  values = [(
      s['strategyId'],
      s['strategyName'],
      s['workspace'],
      s['account'],
      s['brokerProfile'],
      s['symbol'],
      s['symbolRoot'],
      s['exchange'],
      s['currency'],
      s['regDate']
    ) for s in strategies]
  sql = '''
      INSERT OR REPLACE INTO strategies
      (strategyId, strategyName, workspace, account, brokerProfile, symbol, symbolRoot, exchange, currency, regDate)
      VALUES (?,?,?,?,?,?,?,?,?,?)
    '''
  try:
    inserted = mutate_many(sql, values)
    return inserted
  except Exception as e:
    for strategy in strategies:
      print(strategy)
    print('Error trying to save strategies:', repr(e))
  return False
