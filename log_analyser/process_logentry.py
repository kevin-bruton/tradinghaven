from datetime import datetime

strategies = []
orders = []

def _tsToStr(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def _logtimeToTs(str):
  return datetime.strptime(str, '%d.%m.%Y/%H:%M:%S.%f').timestamp()

def _getKeyValue(content, key):
  key_idx = content.find(key)
  if key_idx == -1:
    return ''
  value_idx = key_idx + len(key) + 1
  value_end_idx = content.find(';', value_idx)
  return content[value_idx:value_end_idx]

def _isStrategyIdentifier(content):
  columns = content.split(';')
  return len(columns) > 50 \
    and '@' in columns[2]

def _processStrategyIdentifier(logentry_ts, content):
  global strategies
  columns = content.split(';')
  strategyId = columns[1]
  strategyName = columns[44][1:-1]
  workspace = columns[43][1:-1]
  account = columns[42][1:-1]
  brokerProfile = columns[41][1:-1]
  symbol = columns[36].strip()
  symbolRoot = columns[32][1:-1]
  exchange = columns[35].strip()
  currency = columns[34].strip()
  found_strategies = [s for s in strategies if s['strategyId'] == strategyId]
  if len(found_strategies) == 0:
    strategies.append({
      'strategyId': strategyId,
      'strategyName': strategyName,
      'workspace': workspace,
      'account': account,
      'brokerProfile': brokerProfile,
      'symbol': symbol,
      'symbolRoot': symbolRoot,
      'exchange': exchange,
      'currency': currency,
      'regDate': _tsToStr(logentry_ts)
      })
  
def _isOnorderEvent(content):
  columns = content.split(' ')
  return len(columns) > 0 \
    and columns[0] == 'CProfile::OnOrder'

def _processOnorderEvent(content):
  global orders
  orderId = _getKeyValue(content, 'BrIDStr')
  foundOrders = [o for o in orders if o['orderId'] == orderId]
  if len(foundOrders) == 0:
    order = { 'orderId': orderId }
    orders.append(order)
    foundOrders = [order]
  order = foundOrders[0]
  order['strategyId'] = _getKeyValue(content, 'ELTraderID')
  order['generated'] = _getKeyValue(content, 'Gen')
  order['final'] = _getKeyValue(content, 'Final')
  order['state'] = _getKeyValue(content, 'State')
  order['fillQty'] = int(_getKeyValue(content, 'FillQty'))
  order['fillPrice'] = float(_getKeyValue(content, 'FillPrice'))
  

def processLogentry(logentry_ts, content):
  if _isStrategyIdentifier(content):
    _processStrategyIdentifier(logentry_ts, content)
  elif _isOnorderEvent(content):
    _processOnorderEvent(content)

def getOrders():
  global orders
  temp_orders = orders
  orders = []
  return temp_orders

def getStrategies():
  global strategies
  temp_strategies = strategies
  strategies = []
  return temp_strategies
