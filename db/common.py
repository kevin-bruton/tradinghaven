import sys
import sqlite3
from utils.config import get_config_value

db_path = get_config_value('database_directory') + '/haven.db'

def mutate_one(sql, values: tuple):
  ''' UPDATE, INSERT, DELETE'''
  conn = sqlite3.connect(db_path)
  rows_affected = 0
  try:
    c = conn.cursor()
    c.execute(sql, values)
    conn.commit()
    rows_affected = c.rowcount
  finally:
    conn.close()
  return rows_affected

def mutate_many(sql, values: list[tuple]):
  ''' UPDATE, INSERT, DELETE'''
  conn = sqlite3.connect(db_path)
  rows_affected = 0
  try:
    c = conn.cursor()
    c.executemany(sql, values)
    conn.commit()
    rows_affected = c.rowcount
  finally:
    conn.close()
  return rows_affected

def query_one(sql, values):
  conn = sqlite3.connect(db_path)
  try:
    c = conn.cursor()
    c.execute(sql, values)
    result = c.fetchone()
    return result
  finally:
    conn.close()


def query_many(sql, values: list[tuple]):
  conn = sqlite3.connect(db_path)
  try:
    c = conn.cursor()
    c.execute(sql, values)
    result = c.fetchall()
    return result
  finally:
    conn.close()

def init_db():
  try:
    conn = sqlite3.connect(db_path)
  except sqlite3.Error as e:
    print('ERROR: Could not create or connect to the database.\n')
    print(f'Make sure the following directory exists: {get_config_value("database_directory")}')
    print('as that is the directory you have specified in your config file.')
    print('Make sure you have write permissions to that directory.')
    input('\nPress any key to exit...')
    sys.exit(1)
  try:
    c = conn.cursor()
    c.execute('''
      CREATE TABLE IF NOT EXISTS orders
        (
          br_id PRIMARY KEY,
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
          FOREIGN KEY (strategy_name) REFERENCES strategies (strategy_name)
        );
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
        SELECT name FROM sqlite_master WHERE type='trigger' AND name='insert_strategy';
      ''')
    if c.fetchone() is None:
      c.execute('''
        CREATE TRIGGER insert_strategy
        BEFORE INSERT ON orders
        FOR EACH ROW
        BEGIN
          INSERT OR IGNORE INTO strategies (strategy_name) VALUES (NEW.strategy_name);
        END;
        ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS symbols
        (symbol PRIMARY KEY, contract, min_avg_trade, slippage, tick_size, tick_value, margin, multiplier, exchange);
      ''')
    c.execute('''
      CREATE TABLE IF NOT EXISTS timestamps
        (type PRIMARY KEY, timestamp);
      ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS connection_events
        (id PRIMARY KEY, ts, type, connected);
      ''')
    conn.commit()
  finally:
    conn.close()
