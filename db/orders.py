from .common import mutate_many, mutate_one, query_one

def get_order(orderId):
  sql = '''
    SELECT
      orderId,
      strategyName,
      brokerProfile,
      execTime,
      symbol,
      execQty,
      commission,
      realizedPnl
    FROM orders
    INNER JOIN strategies
    ON strategies.strategyId = orders.strategyId
    WHERE orderId = ?
    '''
  return query_one(sql, (orderId,))

def get_last_filled_order_id():
  sql = '''
      SELECT orderId, MAX(last_update)
      FROM orders
    '''
  result = query_one(sql)
  if len(result):
    return result[0]
  return None

def save_ib_orders(executions):
  orders = executions.values()
  values = [(
    int(o['orderId']),
    o['execTime'] if 'execTime' in o else None,
    o['action'] if 'action' in o else None,
    o['execQty'] if 'execQty' in o else None,
    o['execPrice'] if 'execPrice' in o else None,
    o['orderType'] if 'orderType' in o else None,
    o['stopPrice'] if 'stopPrice' in o else None,
    o['limitPrice'] if 'limitPrice' in o else None,
    o['commission'] if 'commission' in o else None,
    o['realizedPnl'] if 'realizedPnl' in o else None,
    o['execTime'] if 'execTime' in o else None,
    o['action'] if 'action' in o else None,
    o['execQty'] if 'execQty' in o else None,
    o['execPrice'] if 'execPrice' in o else None,
    o['orderType'] if 'orderType' in o else None,
    o['stopPrice'] if 'stopPrice' in o else None,
    o['limitPrice'] if 'limitPrice' in o else None,
    o['commission'] if 'commission' in o else None,
    o['realizedPnl'] if 'realizedPnl' in o else None
  ) for o in orders]
  sql = '''
    INSERT INTO orders
      (
        orderId,
        execTime,
        action,
        execQty,
        execPrice,
        orderType,
        stopPrice,
        limitPrice,
        commission,
        realizedPnl
      )
    VALUES(?,?,?,?,?,?,?,?,?,?)
    ON CONFLICT(orderId) DO
    UPDATE SET
      execTime=?,
      action=?,
      execQty=?,
      execPrice=?,
      orderType=?,
      stopPrice=?,
      limitPrice=?,
      commission=?,
      realizedPnl=?;
  '''
  try:
    result = mutate_many(sql, values)
    return result
  except Exception as e:
    print('  *** Error trying to save orders:', e)
    for order in orders:
      print(order)
    return 0

def save_log_orders(orders: list[dict]):
  values = [(
      int(o['orderId']),
      o['strategyId'] if 'strategyId' in o else None,
      o['generated'] if 'generated' in o else None,
      o['final'] if 'final' in o else None,
      o['fillQty'] if 'fillQty' in o else None,
      o['fillPrice'] if 'fillPrice' in o else None,
      o['state'] if 'state' in o else None
    ) for o in orders if o['state'] == 'Filled']
  sql = '''
    INSERT OR REPLACE INTO orders
      (
        orderId,
        strategyId,
        generated,
        final,
        fillQty,
        fillPrice,
        state
      )
    VALUES(?,?,?,?,?,?,?)
  '''
  try:
    result = mutate_many(sql, values)
    return result
  except Exception as e:
    print('  *** Error trying to save orders:', e)
    for order in orders:
      print(order)
    return 0
