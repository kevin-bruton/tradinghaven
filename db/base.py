import sqlite3

db_path = './data/haven.db'

def insert_one(sql, values):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute(sql, tuple(values))
  conn.commit()
  conn.close()

def insert_many(sql, values):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.executemany(sql, tuple(values))
  conn.commit()
  conn.close()

def select_one(sql, values):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute(sql, tuple(values))
  result = c.fetchone()
  conn.close()
  return result

def select_many(sql, values):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute(sql, tuple(values))
  result = c.fetchall()
  conn.close()
  return result

def update_one(sql, values):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute(sql, tuple(values))
  conn.commit()
  conn.close()

def update_many(sql, values):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.executemany(sql, tuple(values))
  conn.commit()
  conn.close()
