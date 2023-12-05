from .common import mutate_many

def save_positions(positions: list[dict]):
  values = [(
      p['br_id'],
      p['br_id_str'],
      p['strategy_name'],
      p['order_name'],
      p['account'],
      p['symbol'],
      p['exchange'],
      p['contract'],
      p['broker_profile'],
      p['strat_state'],
      p['opl'],
      p['realized_pl'],
      p['generated'],
      p['final'],
      p['action'],
      p['order_type'],
      p['qty'],
      p['price'],
      p['state'],
      p['fill_qty'],
      p['fill_price']
  ) for p in positions]
  sql = '''
    INSERT OR IGNORE INTO positions
      (br_id, br_id_str, strategy_name, order_name, account, symbol, exchange, contract, broker_profile, strat_state, opl, realized_pl, generated, final, action, order_type, qty, price, state, fill_qty, fill_price)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
  '''
  mutate_many(sql, values)
