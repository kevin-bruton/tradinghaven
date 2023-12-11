from .common import mutate_many, query_one

def get_order(br_id):
  sql = '''
      SELECT * FROM orders WHERE br_id = ?
    '''
  return query_one(sql, (br_id,))

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
      o['strat_state'],
      o['opl'],
      o['realized_pl'],
      o['generated'],
      o['final'],
      o['action'],
      o['order_type'],
      o['qty'],
      o['price'],
      o['state'],
      o['fill_qty'],
      o['fill_price']
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
        fill_price
      )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
  '''
  return mutate_many(sql, values)
