import sqlite3

conn = sqlite3.connect('./data/haven.db')
c = conn.cursor()
c.execute('''
  CREATE TABLE orders
    (br_id, br_id_str, strategy_name, order_name, account, symbol, exchange, contract, broker_profile, strat_state, opl, realized_pl, generated, final, action, order_type, qty, price, state, fill_qty, fill_price);
  ''')
c.execute('''
  CREATE TABLE positions
    (br_id, br_id_str, strategy_name, order_name, account, symbol, exchange, contract, broker_profile, strat_state, opl, realized_pl, generated, final, action, order_type, qty, price, state, fill_qty, fill_price);
  ''')
c.execute('''
  CREATE TABLE strategies
    (strategy_name, description, symbols, type, timeframes);
  ''')
c.execute('''
  CREATE TABLE symbols
    (symbol, contract, min_avg_trade, slippage, tick_size, tick_value, margin, multiplier, exchange);
  ''')
conn.commit()
conn.close()
