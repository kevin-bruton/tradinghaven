from .common import mutate_many, query_one

def get_order(br_id):
  sql = 'SELECT * FROM orders WHERE br_id = ?'
  return query_one(sql, (br_id,))

def get_last_filled_order_id():
  sql = '''
      SELECT br_id, MAX(last_update)
      FROM orders
    '''
  result = query_one(sql)
  if len(result):
    return result[0]
  return None

def save_orders(orders: list[dict]):
  values = [(
      o['br_id'],
      o['br_id_str'] if 'br_id_str' in o else None,
      o['trader_id'] if 'trader_id' in o else None,
      o['el_trader_id'] if 'el_trader_id' in o else None,
      o['strategy_name'] if 'strategy_name' in o else None,
      o['order_name'] if 'order_name' in o else None,
      o['account'] if 'account' in o else None,
      o['symbol'] if 'symbol' in o else None,
      o['exchange'] if 'exchange' in o else None,
      o['contract'] if 'contract' in o else None,
      o['broker_profile'] if 'broker_profile' in o else None,
      o['opl'] if 'opl' in o else None,
      o['realized_pl'] if 'realized_pl' in o else None,
      o['generated'] if 'generated' in o else None,
      o['final'] if 'final' in o else None,
      o['action'] if 'action' in o else None,
      o['order_type'] if 'order_type' in o else None,
      o['qty'] if 'qty' in o else None,
      o['price'] if 'price' in o else None,
      o['state'] if 'state' in o else None,
      o['fill_qty'] if 'fill_qty' in o else None,
      o['cur_price'] if 'cur_price' in o else None,
      o['fill_price'] if 'fill_price' in o else None,
      o['last_update']
    ) for o in orders]
  sql = '''
    INSERT OR REPLACE INTO orders
      (
        br_id,
        br_id_str,
        el_trader_id,
        trader_id,
        strategy_name,
        order_name,
        account,
        symbol,
        exchange,
        contract,
        broker_profile,
        opl,
        realized_pl,
        generated,
        final,
        action,
        order_type,
        qty,
        price,
        state,
        fill_qty,
        cur_price,
        fill_price,
        last_update
      )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
  '''
  try:
    result = mutate_many(sql, values)
    return result
  except Exception as e:
    print('  *** Error trying to save orders:', e)
    for order in orders:
      print(order)
    return 0
