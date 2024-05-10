from datetime import datetime, timedelta
import time
import asyncio
from ib_insync import *
from log_analyser.read_logs import read_latest_log
from db.orders import save_ib_orders, get_order
from utils.telegram import send_position_message
from api.ib_requests import get_req, set_res
from ib.contracts import contract

saved_execution_ids = []

def run_ib():
  def _processFills(fills):
    global saved_execution_ids
    # Read latest logfile and save new entries
    time.sleep(1)
    read_latest_log()
    time.sleep(1) 
    # only process executions that have not already been saved
    fills = [f for f in fills if f.execution.execId not in saved_execution_ids]

    executions = []
    for f in fills:
      brokerId = int(f.execution.orderId)
      symbolRoot = f.contract.symbol
      execTime = f.execution.time
      action = f.execution.side
      execQty = f.execution.shares
      execPrice = f.execution.price
      orderRef = f.execution.orderRef
      if len(orderRef):
        rawStopPrice = float(orderRef.split(',')[7].split(':')[1].strip()) if len(orderRef.split(',')) > 7 else 0 
        rawLimitPrice = float(orderRef.split(',')[8].split(':')[1].strip()) if len(orderRef.split(',')) > 7 else 0
        orderType = orderRef.split(',')[5].split(':')[1].strip() if len(orderRef.split(',')) > 7 else 0 
        stopPrice = rawStopPrice if str(rawStopPrice)[-5:] != 'e+308' else 0
        limitPrice = rawLimitPrice if str(rawLimitPrice)[-5:] != 'e+308' else 0
      else:
        orderType = 'Not MC'
        stopPrice = 'Not MC'
        limitPrice = 'Not MC'
      commission = f.commissionReport.commission
      realizedPnl = f.commissionReport.realizedPNL
      execution = {
        "brokerId": brokerId,
        "symbolRoot": symbolRoot,
        "execTime": execTime,
        "action": action,
        "execQty": execQty,
        "execPrice": execPrice,
        "orderType": orderType,
        "stopPrice": stopPrice,
        "limitPrice": limitPrice,
        "commission": commission,
        "realizedPnl": realizedPnl,
        "symbolRoot": symbolRoot,
        "execTime": execTime,
        "action": action,
        "execQty": execQty,
        "execPrice": execPrice,
        "orderType": orderType,
        "stopPrice": stopPrice,
        "limitPrice": limitPrice,
        "commission": commission,
        "realizedPnl": realizedPnl
      }
      executions.append(execution)
    # Save IB order information in the orders table 
    #   (update entries with the same orderId)
    saved = save_ib_orders(executions)
    if saved == len(fills):
      saved_fill_ids = [f.execution.execId for f in fills]
      saved_execution_ids.extend(saved_fill_ids)
    print('Saved', saved, 'IB Execution Orders. brokerId:', fills[0].execution.orderId)  
    # Send Telegram message about the order execution
    #   when realizedPnl != 0
    #print('Num fills:', len(fills), fills[0] if len(fills) == 1 else '')
    if len(fills) == 1:
      _sendExecutionMessage(fills[0])

  def _sendExecutionMessage(fill):
    print('_sendExecutionMessage. brokerId:', fill.execution.orderId, '; realizedPnl:', fill.commissionReport.realizedPNL)
    if fill.commissionReport.realizedPNL != 0:
      order = get_order(fill.execution.orderId)
      print('_sendExecutionMessage. order:', order)
      #send_position_message(order)

  def _executionPerformed(trade, fill):
    print('\nCaught executionDetailEvent', fill.contract.symbol, fill.execution.side, fill.execution.shares, fill.commissionReport.realizedPNL)
    #print('TRADE:', trade)
    #print('FILLS:', ib.fills())
    _processFills([fill])

  def _commissionReported(trade, fill, commissionReport):
    #time.sleep(1)
    print('\nCaught commissionReportEvent', fill.contract.symbol, fill.execution.side, fill.execution.shares, 'profit:', commissionReport.realizedPNL, 'orderId:', fill.execution.orderId)
    _processFills([fill])


  def _process_api_request(api_request):
    if api_request['name'] == 'accounts':
      print('isConnected:', ib.isConnected())
      accounts = ib.managedAccounts()
      set_res('accounts', accounts)
    elif api_request['name'] == 'data':
      year = int(api_request['day_YYYYMMDD'][:4])
      month = int(api_request['day_YYYYMMDD'][4:6])
      day = int(api_request['day_YYYYMMDD'][6:8])
      end_dt = datetime(year, month, day, 23, 59, 59)
      print('Requesting IB for data. Symbol:', api_request['symbol'], 'Date:', end_dt)
      #def errorHandler(reqId, errorCode, errorString, contract):
      #  print('Data Error Handler:', reqId, errorCode, errorString)
      #ib.errorEvent += errorHandler
      bars = ib.reqHistoricalData(
        contract(api_request['symbol']),
        endDateTime=end_dt,
        durationStr='1 D',
        barSizeSetting='1 min',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1
      )
      print('Num bars received:', len(bars))

      only_bars_on_the_day = [b for b in bars if b.date.strftime('%Y-%m-%d') == datetime(year, month, day).strftime('%Y-%m-%d')]
      set_res('data', only_bars_on_the_day)

  try:
    loop = asyncio.get_event_loop()
  except RuntimeError as e:
    if str(e).startswith('There is no current event loop in thread'):
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
    else:
        raise
  
  ib = IB()
  ib.connect('127.0.0.1', 4002, clientId=3)
  print('********************************************')
  print('            CONNECTED TO IB')
  print('********************************************')
  fills = ib.fills()
  _processFills(fills)
  #ib.execDetailsEvent += _executionPerformed
  ib.commissionReportEvent += _commissionReported

  while True:
    try:
      ib.sleep(1)
      api_request = get_req()
      if api_request != None:
        _process_api_request(api_request)
    except Exception as e:
      print(repr)
  ibTrader.disconnect()
