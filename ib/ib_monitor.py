import time
import asyncio
from ib_insync import *
from log_analyser.read_logs import read_latest_log
from db.orders import save_ib_orders, get_order
from utils.telegram import send_position_message
from api.ib_requests import get_req, set_res

saved_execution_ids = []

def run_ib():
  def _processFills(fills):
    global saved_execution_ids
    # Read latest logfile and save new entries
    read_latest_log()
    # only process executions that have not already been saved
    fills = [f for f in fills if f.execution.execId not in saved_execution_ids]

    executions = []
    for f in fills:
      orderId = int(f.execution.orderId)
      symbolRoot = f.contract.symbol
      execTime = f.execution.time
      action = f.execution.side
      execQty = f.execution.shares
      execPrice = f.execution.price
      orderRef = f.execution.orderRef
      if len(orderRef):
        rawStopPrice = float(orderRef.split(',')[7].split(':')[1].strip())
        rawLimitPrice = float(orderRef.split(',')[8].split(':')[1].strip())
        orderType = orderRef.split(',')[5].split(':')[1].strip()
        stopPrice = rawStopPrice if str(rawStopPrice)[-5:] != 'e+308' else 0
        limitPrice = rawLimitPrice if str(rawLimitPrice)[-5:] != 'e+308' else 0
      else:
        orderType = 'Not MC'
        stopPrice = 'Not MC'
        limitPrice = 'Not MC'
      commission = f.commissionReport.commission
      realizedPnl = f.commissionReport.realizedPNL
      fill = (
        orderId,
        symbolRoot,
        execTime,
        action,
        execQty,
        execPrice,
        orderType,
        stopPrice,
        limitPrice,
        commission,
        realizedPnl,
        symbolRoot,
        execTime,
        action,
        execQty,
        execPrice,
        orderType,
        stopPrice,
        limitPrice,
        commission,
        realizedPnl
      )
      executions.append(fill)
    # Save IB order information in the orders table 
    #   (update entries with the same orderId)
    saved = save_ib_orders(executions)
    if saved == len(fills):
      saved_fill_ids = [f.execution.execId for f in fills]
      saved_execution_ids.extend(saved_fill_ids)
    print('Saved', saved, 'IB Execution Orders')
    # Send Telegram message about the order execution
    #   when realizedPnl != 0
    #print('Num fills:', len(fills), fills[0] if len(fills) == 1 else '')
    if len(fills) == 1:
      _sendExecutionMessage(fills[0])

  def _sendExecutionMessage(fill):
    print('_sendExecutionMessage. realizedPnl:', fill.commissionReport.realizedPNL)
    if fill.commissionReport.realizedPNL != 0:
      order = get_order(fill.execution.orderId)
      print('_sendExecutionMessage. order:', order)
      send_position_message(order)

  def _executionPerformed(trade, fill):
    print('Caught executionDetailEvent', fill.contract.symbol, fill.execution.side, fill.execution.shares)
    _processFills([fill])

  def _process_api_request(api_request):
    if api_request == 'accounts':
      accounts = ib.managedAccounts()
      set_res('accounts', accounts)

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
  fills = ib.fills()
  _processFills(fills)
  ib.execDetailsEvent += _executionPerformed

  while True:
    try:
      ib.sleep(1)
      api_request = get_req()
      if api_request != None:
        _process_api_request(api_request)
    except Exception as e:
      print(repr)
  ibTrader.disconnect()
