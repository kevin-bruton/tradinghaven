from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time
from datetime import datetime, timedelta
from ib.contracts import contract
import os

from ib.ib_client import IbClient

date_fmt = "%Y%m%d-%H:%M:%S"

class IbTrader():
  def __init__(self, port=4002):
    self.ibClient = IbClient()
    self.ibClient.connect(host='127.0.0.1', port=port, clientId=2) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
    self.conThread = threading.Thread(target=self.ibClient.run)
    self.conThread.start()

    time.sleep(2) # Give time to connect...
    print()

  def disconnect(self):
    self.ibClient.disconnect()

  def getContract(self, symbol):
    return self.ibClient.getContractDetails(symbol)
  
  def getOrderExecutions(self):
    return self.ibClient.getOrderExecutions()
  
  def getCompletedOrders(self):
    return self.ibClient.getCompletedOrders()
  
  def subscribeToPositions(self, gotPosition):
    self.ibClient.subscribeToPositions(gotPosition)

"""
def gotExecution(execution):
  print('\nGot Execution:\n', execution)

if __name__ == '__main__':
  ibTrader = IbTrader()
  resp = ibTrader.getContract('DAX')
  print('RESPONSE:\n', resp)
  ibTrader.subscribeToOrderExecutions(gotExecution)
  while True:
    time.sleep(1)
  ibTrader.disconnect()
"""