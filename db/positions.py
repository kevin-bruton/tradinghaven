from .common import mutate_many

def save_positions(positions: list[dict]):
  values = [(
      p['br_id'],
      p['br_id_str'] if 'br_id_str' in p else None,
      p['el_trader_id'] if 'el_trader_id' in p else None,
      p['trader_id'] if 'trader_id' in p else None,
      p['strategy_name'] if 'strategy_name' in p else None,
      p['order_name'] if 'order_name' in p else None,
      p['account'] if 'account' in p else None,
      p['symbol'] if 'symbol' in p else None,
      p['exchange'] if 'exchange' in p else None,
      p['contract'] if 'contract' in p else None,
      p['broker_profile'] if 'broker_profile' in p else None,
      p['strat_state'] if 'strat_state' in p else None,
      p['opl'] if 'opl' in p else None,
      p['realized_pl'] if 'realized_pl' in p else None,
      p['generated'] if 'generated' in p else None,
      p['final'] if 'final' in p else None,
      p['action'] if 'action' in p else None,
      p['order_type'] if 'order_type' in p else None,
      p['qty'] if 'qty' in p else None,
      p['price'] if 'price' in p else None,
      p['state'] if 'state' in p else None,
      p['fill_qty'] if 'fill_qty' in p else None,
      p['fill_price'] if 'fill_price' in p else None,
      p['last_update']
  ) for p in positions]
  sql = '''
    INSERT OR IGNORE INTO positions
      (br_id, br_id_str, el_trader_id, trader_id, strategy_name, order_name, account, symbol, exchange, contract, broker_profile, strat_state, opl, realized_pl, generated, final, action, order_type, qty, price, state, fill_qty, fill_price, last_update)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
  '''
  return mutate_many(sql, values)
