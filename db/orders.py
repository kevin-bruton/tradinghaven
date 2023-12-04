from base import insert_many

def save_orders(orders):
  sql = '''
    INSERT INTO orders
      (br_id, br_id_str, strategy_name, order_name, account, symbol, exchange, contract, broker_profile, strat_state, opl, realized_pl, generated, final, action, order_type, qty, price, state, fill_qty, fill_price)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
  '''
  insert_many(sql, orders)
