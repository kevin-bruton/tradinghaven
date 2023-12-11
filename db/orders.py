from .common import mutate_many, query_one

def get_order(br_id):
  sql = '''
      SELECT * FROM orders WHERE br_id = ?
    '''
  return query_one(sql, (br_id,))

def get_last_filled_order_id():
  sql = '''
      SELECT br_id, MAX(last_update)
      FROM orders
    '''
  return query_one(sql)

def save_orders(orders: list[dict]):
  values = [(
      o['br_id'],
      o['br_id_str'],
      o['strategy_name'],
      o['order_name'],
      o['account'],
      o['symbol'],
      o['exchange'],
      o['contract'],
      o['broker_profile'],
      o['strat_state'] if 'strat_state' in o else None,
      o['opl'] if 'opl' in o else None,
      o['realized_pl'] if 'realized_pl' in o else None,
      o['generated'] if 'geerated' in o else None,
      o['final'] if 'final' in o else None,
      o['action'] if 'action' in o else None,
      o['order_type'] if 'order_type' in o else None,
      o['qty'] if 'qty' in o else None,
      o['price'] if 'price' in o else None,
      o['state'] if 'state' in o else None,
      o['fill_qty'] if 'fill_qty' in o else None,
      o['fill_price'] if 'fill_price' in o else None,
      o['last_update']
    ) for o in orders]
  sql = '''
    INSERT OR REPLACE INTO orders
      (
        br_id,
        br_id_str,
        strategy_name,
        order_name,
        account,
        symbol,
        exchange,
        contract,
        broker_profile,
        strat_state,
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
        fill_price,
        last_update
      )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
  '''
  return mutate_many(sql, values)
