from threading import Lock
from queue import Queue

lock = Lock()
reqs = []
resps = {}

def get_req():
  global reqs
  with lock:
    if len(reqs) == 0:
      return None
    return reqs.pop(0)

def get_res(key):
  global resps
  with lock:
    if key in resps:
      resp = resps[key]
      del resps[key]
      return resp
    return None

def set_req(api_req):
  global reqs
  with lock:
    reqs.append(api_req)

def set_res(key, api_res):
  global resps
  with lock:
    resps[key] = api_res
