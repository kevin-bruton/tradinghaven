import sqlite3
from utils.config import get_config_value

db_path = get_config_value('database_directory') + '/haven.db'

def mutate_one(sql, values: tuple):
  ''' UPDATE, INSERT, DELETE'''
  conn = sqlite3.connect(db_path)
  try:
    c = conn.cursor()
    c.execute(sql, values)
    conn.commit()
  finally:
    conn.close()

def mutate_many(sql, values: list[tuple]):
  ''' UPDATE, INSERT, DELETE'''
  conn = sqlite3.connect(db_path)
  try:
    c = conn.cursor()
    c.executemany(sql, values)
    conn.commit()
  finally:
    conn.close()

def select_one(sql, values):
  conn = sqlite3.connect(db_path)
  try:
    c = conn.cursor()
    c.execute(sql, values)
    result = c.fetchone()
    return result
  finally:
    conn.close()


def select_many(sql, values: list[tuple]):
  conn = sqlite3.connect(db_path)
  try:
    c = conn.cursor()
    c.execute(sql, values)
    result = c.fetchall()
    return result
  finally:
    conn.close()

def init_db():
  conn = sqlite3.connect(db_path)
  try:
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS orders
        (br_id PRIMARY KEY, br_id_str, strategy_name, order_name, account, symbol, exchange, contract, broker_profile, strat_state, opl, realized_pl, generated, final, action, order_type, qty, price, state, fill_qty, fill_price);
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS positions
        (br_id PRIMARY KEY, br_id_str, strategy_name, order_name, account, symbol, exchange, contract, broker_profile, strat_state, opl, realized_pl, generated, final, action, order_type, qty, price, state, fill_qty, fill_price);
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS strategies
        (strategy_name PRIMARY KEY, description, symbols, type, timeframes);
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS symbols
        (symbol PRIMARY KEY, contract, min_avg_trade, slippage, tick_size, tick_value, margin, multiplier, exchange);
      ''')
    conn.commit()
  finally:
    conn.close()
