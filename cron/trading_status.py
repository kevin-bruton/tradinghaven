import json
import time
from os import listdir
from os.path import isfile, join
from datetime import datetime
from db.connection_events import save_connection_events
from db.timestamps import get_timestamp, save_timestamp
from utils.config import get_config_value
from utils.telegram import send_message

positionMismatches = {}

def logStrategyConnections(ts, accountId, strategyName, isEnabled):
  log_entry = tsToStr(ts) + ' - ' + accountId + ' - ' + strategyName + ' - Auto Trading ' + ('Enabled' if isEnabled else 'Disabled')
  with open(get_config_value('log_dir') + 'strategy_connections.log', 'a') as f:
    f.write(log_entry + '\n')

def logDataConnections(ts, isConnected):
  log_entry = tsToStr(ts) + ' - Data ' + ('Connected' if isConnected else 'Disconnected')
  with open(get_config_value('log_dir') + 'data_connections.log', 'a') as f:
    f.write(log_entry + '\n')
  
def logStrategyPositionChanges(ts, accountId, strategyName, message):
  log_entry = tsToStr(ts) + ' - ' + message
  with open(get_config_value('log_dir') + f'position_changes-{accountId}-{strategyName}.log', 'a') as f:
    f.write(log_entry + '\n')

def logPositionMismatch(ts, message):
  log_entry = tsToStr(ts) + ' - ' + message
  with open(get_config_value('log_dir') + 'position_mismatches.log', 'a') as f:
    f.write(log_entry + '\n')

def tsToStr(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def tsToMsgTs(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M.%S')

def logtimeToTs(str):
  return datetime.strptime(str, '%d.%m.%Y/%H:%M:%S.%f').timestamp()

def sendConnectionMessage(ts, message):
  if get_config_value('send_connection_messages'):
    msg = f"""LIVE TRADING UPDATE:  
      Time: {tsToStr(ts)}  
      Event: {message}"""
    send_message(msg)

def processTradingStatus():
  html = f'''<!DOCTYPE html><html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
      <link rel="icon" href="data:;base64,iVBORw0KGgo=">
      <title>Live Status</title>
    </head>
    <body>
      <nav class="navbar is-info" style="display: flex; align-items: center;">
        <a class="navbar-item">Live</a>
        <a class="navbar-item" style="color: white">Demo</a>
      </nav>
      <div class="container" style="margin: 3px;">
    '''
  brokerUpdateHtml = '<div>Last broker update: '
  strategyUpdateHtml = '<div>Last strategy update: '
  dataConnectionHtml = '<div>Data connection status: '
  symbolStatusHtml = '<br><br><div><strong>POSITIONS</strong></div><table class="table"><thead><tr><th>Symbol</th><th>Broker</th><th>Strategy</th><th>Aligned?</th></tr></thead><tbody>'
  strategyStatusHtml = '<br><br><div><strong>STRATEGIES</strong></h2><table class="table"><thead><tr><th>Strategy Name</th><th>Auto Trading</th><th>Mkt Position</th><th>Profit</th><th>Profit Factor</th><th>Ret/DD</th><th>Num Trades</th></tr></thead><tbody>'
  ts = datetime.now().timestamp()
  #print(tsToStr(ts) + ' - Processing trading status...')
  status_dir = get_config_value('mc_status_dir')
  onlyfiles = [f for f in listdir(status_dir) if isfile(join(status_dir, f))]
  brokerPositions = {}
  strategyPositions = {}
  for file in onlyfiles:
    didReadFile = False
    try:
      with open(join(status_dir, file), 'r') as f:
        content = json.loads(f.read())
        didReadFile = True
    except:
      time.sleep(1)
    if not didReadFile:
      try:
        with open(join(status_dir, file), 'r') as f:
          content = json.loads(f.read())
          didReadFile = True
      except Exception as e:
        print(tsToStr(ts) + ' - Error reading file ' + file + ': ' + str(e))
        continue
    if file == 'broker_status.json':
      brokerUpdateHtml += content['computerDatetime'] + '</div>'
      dataConnectionHtml += '<span class="tag is-success">OK</span>' \
        if content['dataConnectionOk'] \
        else '<span class="tag is-danger">NOK</span>' + '</div>'
      # Check for data connection status changes
      if content['lastDataConnectionOk'] and not content['dataConnectionOk']:
        sendConnectionMessage(ts, 'Data connection lost')
        logDataConnections(ts, False)
      elif not content['lastDataConnectionOk'] and content['dataConnectionOk']:
        sendConnectionMessage(ts, 'Data connection restored')
        logDataConnections(ts, True)
      # Get broker positions
      for account in content['accounts']:
        accountId = account['accountId']
        if accountId != "":
          for symbol in account['symbols']:
            if accountId not in brokerPositions:
              brokerPositions[accountId] = {}
            brokerPositions[accountId][symbol] = int(account['symbols'][symbol])
    else:
      accountId = content['accountId']
      symbol = content['symbol']
      strategyName = content['strategyName']
      if len(strategyUpdateHtml) < 30:
        strategyUpdateHtml += content['computerDatetime'] + '</div>'
      strategyStatusHtml += f'<tr><td>{strategyName}</td><td>'
      strategyStatusHtml +='<span class="tag is-success">OK</span>' if content["autoTradingEnabled"] else '<span class="tag is-danger">NOK</span>'
      #strategyStatusHtml += f'</td><td>{content["position"]}</td>'
      strategyStatusHtml += f'<td>{content["marketPosition"]}</td>'
      strategyStatusHtml += f'<td>{content["netProfit"]}</td>'
      strategyStatusHtml += f'<td>{content["profitFactor"]}</td>'
      strategyStatusHtml += f'<td>{content["retDd"]}</td>'
      strategyStatusHtml += f'<td>{content["numTrades"]}</td></tr>'
      # Get strategy positions
      if accountId not in strategyPositions:
        strategyPositions[accountId] = {}
      if symbol not in strategyPositions[accountId]:
        strategyPositions[accountId][symbol] = 0
      strategyPositions[accountId][symbol] += content['marketPosition']
      # Check for strategy position changes
      if content['marketPosition'] != content['lastMarketPosition']:
        msg1 = f'Position change detected.'
        msg2 = f'{accountId} - {symbol} - {strategyName}.'
        msg3 = f"{content['lastMarketPosition']} -> {content['marketPosition']}"
        sendConnectionMessage(ts, f'{msg1}\n  {msg2}\n  {msg3}')
        logStrategyPositionChanges(ts, accountId, strategyName, msg1 + ' ' + msg2 + ' ' + msg3)
      # Check for auto trading status changes
      if content['lastAutoTradingEnabled'] and not content['autoTradingEnabled']:
        msg = f'{accountId} - {symbol} - {strategyName}\n  Auto trading disabled.'
        sendConnectionMessage(ts, msg)
        logStrategyConnections(ts, accountId, strategyName, False)
      elif not content['lastAutoTradingEnabled'] and content['autoTradingEnabled']:
        msg = f'{accountId} - {symbol} - {strategyName}\n  Auto trading enabled.'
        sendConnectionMessage(ts, msg)
        logStrategyConnections(ts, accountId, strategyName, True)

  # Check for position mismatches
  for accountId in strategyPositions:
    for symbol in strategyPositions[accountId]:
      symbolStatusHtml += f'<tr><td>{symbol}</td><td>{brokerPositions[accountId][symbol]}</td><td>{strategyPositions[accountId][symbol]}</td><td><span class="tag ' + \
        ('is-success">OK' if brokerPositions[accountId][symbol] == strategyPositions[accountId][symbol] else 'is-danger">NOK') + \
        '</span></td></tr>'
      if symbol not in positionMismatches:
        positionMismatches[symbol] = False
      isPositionMismatch = brokerPositions[accountId][symbol] != strategyPositions[accountId][symbol]
      if isPositionMismatch and not positionMismatches[symbol]:
        positionMismatches[symbol] = True
        msg1 = f'Position mismatch detected.'
        msg2 = f'{accountId} - {symbol}.'
        msg3 = f'Broker position: {brokerPositions[accountId][symbol]}; Strategy position: {strategyPositions[accountId][symbol]}'
        sendConnectionMessage(ts, msg1 + '\n  ' + msg2 + '\n  ' + msg3)
        logPositionMismatch(ts, msg1 + ' ' + msg2 + ' ' + msg3)
      if not isPositionMismatch and positionMismatches[symbol]:
        msg1 = f'Position mismatch resolved.'
        msg2 = f'{accountId} - {symbol}.'
        msg3 = f'Broker position: {brokerPositions[accountId][symbol]}; Strategy position: {strategyPositions[accountId][symbol]}'
        sendConnectionMessage(ts, msg1 + '\n  ' + msg2 + '\n  ' + msg3)	
        logPositionMismatch(ts, msg1 + ' ' + msg2 + ' ' + msg3)
      positionMismatches[symbol] = isPositionMismatch
  html += brokerUpdateHtml + strategyUpdateHtml + dataConnectionHtml + symbolStatusHtml + '</tbody></table>' + strategyStatusHtml + '</tbody></table></div></body></html>'
  with open(get_config_value('log_dir') + 'live_status.html', 'w') as f:
    f.write(html)

      


        
