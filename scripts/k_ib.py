from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

reqId = 10

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 
        
    def historicalData(self, reqId, bar):
        print(f'Time: {bar.date}, Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}')

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        global event
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        event.set()

    def contractDetails(self, reqId: int, contractDetails):
        super().contractDetails(reqId, contractDetails)
        print('Got Contract! Symbol:', contractDetails.contract.symbol)
    
    def contractDetailsEnd(self, reqId: int):
        super().contractDetailsEnd(reqId)
        print("ContractDetailsEnd. ReqId:", reqId)

def daxContract():
    contract = Contract()
    contract.conId = 540729519
    contract.symbol = "DAX"
    contract.secType = "CONTFUT"
    contract.currency = "EUR"
    contract.exchange = "EUREX"
    return contract 

def reqHistData(contract, duration):
    """requests historical data"""
    global reqId
    reqId += 1
    trade_app.reqHistoricalData(
        reqId=reqId, 
        contract=contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting='1 min',
        whatToShow='ADJUSTED_LAST',
        useRTH=1,
        formatDate=1,
        keepUpToDate=0,
        chartOptions=[]
    )

def reqContractDetails(contract):
    global reqId
    reqId += 1
    trade_app.reqContractDetails(reqId=reqId,contract=contract)

#####################################################################################################
    


event = threading.Event()
trade_app = TradeApp()
trade_app.connect(host='127.0.0.1', port=4002, clientId=2) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=trade_app.run)
con_thread.start()

reqHistData(daxContract(), duration='360 S')
print('Request has been made')

while not event.is_set():
    time.sleep(1)

trade_app.disconnect()
print('Done!')
