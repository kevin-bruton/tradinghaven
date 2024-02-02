from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.execution import ExecutionFilter
import threading
import time
from datetime import datetime, timedelta
from ib.contracts import contract
from sys import float_info

class IbClient(EWrapper, EClient): 
  def __init__(self): 
    EClient.__init__(self, self)
    self._ibRequest = threading.Event()
    self._reqId = 10
    self._data = {}
    self._loadedInitialPositions = False
    self._gotPosition = None
    
  def error(self, reqId, errorCode: int, errorString: str, advancedOrderRejectJson = ""):
    # super().error(reqId, errorCode, errorString, advancedOrderRejectJson)
    if reqId == -1:
      print(errorCode, errorString) 
      return
    if errorCode == 162:
      print("  No data for this day")
      self._ibRequest.set()
      return
    if advancedOrderRejectJson:
      print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString, "AdvancedOrderRejectJson:", advancedOrderRejectJson)
    else:
      print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
    self._ibRequest.set()
        
  def historicalData(self, reqId, bar):
    if not reqId or not bar:
      print('No data')
      return
    symbol = self._data[reqId]
    # print(f'{symbol} Time: {bar.date}, Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}')
    date_str = f"{int(bar.date[6:8])}/{bar.date[4:6]}/{bar.date[:4]}"
    time_str = f"{bar.date[9:17]}"
    line = f"{date_str},{time_str},{bar.open},{bar.high},{bar.low},{bar.close},{bar.volume}\n"
    #print('line to add:', line)
    # data += line

  def historicalDataEnd(self, reqId: int, start: str, end: str):
    super().historicalDataEnd(reqId, start, end)
    # print("  HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
    self._ibRequest.set()

  def contractDetails(self, reqId: int, contractDetails):
    super().contractDetails(reqId, contractDetails)
    print('Got Contract! Symbol:', contractDetails.contract.symbol)
    self._data[reqId] = contractDetails.contract
    
  def contractDetailsEnd(self, reqId: int):
    super().contractDetailsEnd(reqId)
    print("ContractDetailsEnd. ReqId:", reqId)
    self._ibRequest.set()
    
  def headTimestamp(self, reqId:int, headTimestamp:str):
    print("HeadTimestamp. ReqId:", reqId, "HeadTimeStamp:", headTimestamp)
    self._ibRequest.set()
 
  def execDetails(self, reqId: int, contract, execution):
    super().execDetails(reqId, contract, execution)
    #print("ExecDetails. ReqId:", reqId, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:", contract.currency, execution)
    print("ExecDetails. reqId:", reqId)
    if reqId not in self._data:
      self._data[reqId] = {}
    execId = execution.execId
    if execId in self._data[reqId]:
      exec = self._data[reqId][execId]
    else:
      exec = {}
    exec['execTime'] = execution.time
    exec['account'] = execution.acctNumber
    exec['exchange'] = execution.exchange
    exec['symbol'] = contract.symbol
    exec['action'] = execution.side
    exec['execQty'] = float(execution.shares)
    exec['execPrice'] = execution.price
    exec['orderId'] = execution.orderId
    orderRef = execution.orderRef
    if len(orderRef):
      stopPrice = float(execution.orderRef.split(',')[7].split(':')[1].strip())
      limitPrice = float(execution.orderRef.split(',')[8].split(':')[1].strip())
      exec['orderType'] = orderRef.split(',')[5].split(':')[1].strip()
      exec['stopPrice'] = stopPrice if str(stopPrice)[-5:] != 'e+308' else 0
      exec['limitPrice'] = limitPrice if str(limitPrice)[-5:] != 'e+308' else 0
    else:
      exec['orderType'] = 'Not MC'
      exec['stopPrice'] = 'Not MC'
      exec['limitPrice'] = 'Not MC'
    self._data[reqId][execId] = exec

  def commissionReport(self, commissionReport):
    super().commissionReport(commissionReport)
    print("CommissionReport.", self._reqId)
    reqId = self._reqId
    if reqId not in self._data:
      self._data[reqId] = {}
    execId = commissionReport.execId
    if execId in self._data[reqId]:
      exec = self._data[reqId][execId]
    else:
      exec = {}
    exec['commission'] = commissionReport.commission
    exec['currency'] = commissionReport.currency
    exec['realizedPnl'] = round(commissionReport.realizedPNL, 2) if str(commissionReport.realizedPNL)[-5:] != 'e+308' else 0
    self._data[reqId][execId] = exec

  def execDetailsEnd(self, reqId):
    print('Finished retrieving historical executions from IB. reqId:', reqId)
    if reqId not in self._data:
      self._data[reqId] = {}
    self._ibRequest.set()

  def position(self, account: str, contract, position, avgCost: float):
    super().position(account, contract, position, avgCost)
    if self._loadedInitialPositions:
      pos= {'account': account, 'qty': int(position)}
      self._gotPosition(pos)

  def positionEnd(self):
    super().positionEnd()
    self._loadedInitialPositions = True

  def completedOrder(self, contract, order, orderState):
    super().completedOrder(contract, order, orderState)
    print('Got completed order:', orderState, order)

  def completedOrdersEnd(self):
    print('Got completed orders end')
    self._ibRequest.set()

  ############################################
  ################ REQUESTS ##################
  ############################################
        
  def getContractDetails(self, symbol):
    reqId = self._reqId + 1
    self._reqId = reqId
    self.reqContractDetails(reqId=reqId,contract=contract(symbol))
    self._ibRequest.wait()
    response = self._data[reqId]
    del self._data[reqId]
    return response
    
  def getOrderExecutions(self):
    reqId = self._reqId + 1
    self._reqId = reqId
    self.reqExecutions(reqId=reqId, execFilter=ExecutionFilter())
    self._ibRequest.wait()
    response = self._data[reqId]
    del self._data[reqId]
    self._ibRequest.clear()
    return response
  
  def getCompletedOrders(self):
    reqId = self._reqId + 1
    self._reqId = reqId
    self.reqCompletedOrders(apiOnly=False)
    #self._ibRequest.wait()
    #self._ibRequest.clear()
    #response = self._data[reqId]
    #del self._data[reqId]
    #return response
  
  def subscribeToPositions(self, gotPosition):
    reqId = self._reqId +1
    self._reqId = reqId
    self._gotPosition = gotPosition
    self.reqPositions()
        