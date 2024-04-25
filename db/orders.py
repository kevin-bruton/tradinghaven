from .common import mutate_many, mutate_one, query_one

def get_order(brokerId):
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
    WHERE brokerId = ?
    '''
  return query_one(sql, (brokerId,))

def get_last_filled_order_id():
  sql = '''
      SELECT orderId, MAX(last_update)
      FROM orders
    '''
  result = query_one(sql)
  if len(result):
    return result[0]
  return None

def save_ib_orders(executions: list[dict]):
  values = [(
      e['symbolRoot'],
      e['execTime'],
      e['action'],
      e['execQty'],
      e['execPrice'],
      e['orderType'],
      e['stopPrice'],
      e['limitPrice'],
      e['commission'],
      e['realizedPnl'],
      e['brokerId']
  ) for e in executions]
  sql = '''
    UPDATE orders
    SET
      symbolRoot=?,
      execTime=?,
      action=?,
      execQty=?,
      execPrice=?,
      orderType=?,
      stopPrice=?,
      limitPrice=?,
      commission=?,
      realizedPnl=?
    WHERE brokerId=?
  '''
  try:
    result = mutate_many(sql, values)
    return result
  except Exception as e:
    print('  *** save_ib_orders. Error trying to save orders:', e)
    return 0

def save_log_orders(orders: list[dict]):
  values = [(
      int(o['orderId']),
      int(o['brokerId']) if 'brokerId' in o else None,
      o['strategyId'] if 'strategyId' in o else None,
      o['generated'] if 'generated' in o else None,
      o['final'] if 'final' in o else None,
      o['fillQty'] if 'fillQty' in o else None,
      o['initialPrice'] if 'initialPrice' in o else None,
      o['fillPrice'] if 'fillPrice' in o else None,
      o['state'] if 'state' in o else None,
      int(o['brokerId']) if 'brokerId' in o else None,
      o['strategyId'] if 'strategyId' in o else None,
      o['generated'] if 'generated' in o else None,
      o['final'] if 'final' in o else None,
      o['fillQty'] if 'fillQty' in o else None,
      o['initialPrice'] if 'initialPrice' in o else None,
      o['fillPrice'] if 'fillPrice' in o else None,
      o['state'] if 'state' in o else None
    ) for o in orders if o['state'] == 'Filled']
  sql = '''
    INSERT INTO orders
      (
        orderId,
        brokerId,
        strategyId,
        generated,
        final,
        fillQty,
        initialPrice,
        fillPrice,
        state
      )
    VALUES(?,?,?,?,?,?,?,?,?)
    ON CONFLICT(orderId) DO
    UPDATE SET
      brokerId=coalesce(?,brokerId),
      strategyId=coalesce(?,strategyId),
      generated=coalesce(?,generated),
      final=coalesce(?,final),
      fillQty=coalesce(?,fillQty),
      initialPrice=coalesce(?,initialPrice),
      fillPrice=coalesce(?,fillPrice),
      state=coalesce(?,state);
  '''
  try:
    result = mutate_many(sql, values)
    return result
  except Exception as e:
    print('  *** save_log_orders. Error trying to save orders:', e)
    for order in orders:
      print(order)
    return 0
