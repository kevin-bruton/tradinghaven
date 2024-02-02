import time
from ib.ib_trader import IbTrader
from log_analyser.read_logs import read_latest_log
from db.orders import save_ib_orders, get_order
from utils.telegram import send_position_message


def run_ib():
  def _processExecutions(executions):
    # Pause to allow for onOrder event to be added to logs:
    time.sleep(5)
    # Read latest logfile and save new entries
    read_latest_log()
    # Save IB order information in the orders table 
    #   (update entries with the same orderId)
    saved = save_ib_orders(executions)
    print('Saved', saved, 'IB Execution Orders')
    # Send Telegram message about the order execution
    #   when realizedPnl != 0

  def _gotPosition(position):
    executions = ibTrader.getOrderExecutions()
    #ibTrader.getCompletedOrders()
    _processExecutions(executions)
    #_sendExecutionMessage(executions)
    print('Got postion:', position)
    pass

  def _sendExecutionMessage(executions):
    for execution in executions:
      if execution['realizedPnl'] != 0:
        order = get_order(execution['orderId'])
        send_position_message(order)

  ibTrader = IbTrader()
  #executions = ibTrader.getOrderExecutions()
  #_processExecutions(executions)
  ibTrader.subscribeToPositions(_gotPosition)
  while True:
    time.sleep(1)
  ibTrader.disconnect()
