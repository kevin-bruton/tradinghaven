from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time
from datetime import datetime, timedelta
from contracts import contract
import os

reqId = 10
date_fmt = "%Y%m%d-%H:%M:%S"
reqId_symbol = {}

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self)
        self.data_requests = {}
    
    def error(self, reqId, errorCode: int, errorString: str, advancedOrderRejectJson = ""):
        # super().error(reqId, errorCode, errorString, advancedOrderRejectJson)
        if reqId == -1:
            print(errorCode, errorString) 
            return
        if errorCode == 162:
          print("  No data for this day")
          ib_request.set()
          return
        if advancedOrderRejectJson:
          print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString, "AdvancedOrderRejectJson:", advancedOrderRejectJson)
        else:
          print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        ib_request.set()
        
    def historicalData(self, reqId, bar):
        global data
        if not reqId or not bar:
            print('No data')
            return
        symbol = reqId_symbol[reqId]
        # print(f'{symbol} Time: {bar.date}, Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}')
        date_str = f"{int(bar.date[6:8])}/{bar.date[4:6]}/{bar.date[:4]}"
        time_str = f"{bar.date[9:17]}"
        line = f"{date_str},{time_str},{bar.open},{bar.high},{bar.low},{bar.close},{bar.volume}\n"
        #print('line to add:', line)
        data += line

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        global event
        super().historicalDataEnd(reqId, start, end)
        # print("  HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        ib_request.set()

    def contractDetails(self, reqId: int, contractDetails):
        super().contractDetails(reqId, contractDetails)
        print('Got Contract! Symbol:', contractDetails.contract.symbol)
    
    def contractDetailsEnd(self, reqId: int):
        super().contractDetailsEnd(reqId)
        print("ContractDetailsEnd. ReqId:", reqId)
        ib_request.set()
    
    def headTimestamp(self, reqId:int, headTimestamp:str):
        print("HeadTimestamp. ReqId:", reqId, "HeadTimeStamp:", headTimestamp)
        ib_request.set()


def reqHistData(contract, endDateTime, duration_str):
    """requests historical data"""
    global reqId
    reqId += 1
    reqId_symbol[reqId] = contract.symbol
    # print('  Requesting data. reqId:', reqId, 'end_dt:', endDateTime)
    trade_app.reqHistoricalData(
        reqId=reqId, 
        contract=contract,
        endDateTime=endDateTime.strftime(date_fmt),
        durationStr=duration_str,
        barSizeSetting='1 min',
        whatToShow='TRADES',
        useRTH=1,
        formatDate=1,
        keepUpToDate=0,
        chartOptions=[]
    )

def reqContractDetails(contract):
    global reqId
    reqId += 1
    trade_app.reqContractDetails(reqId=reqId,contract=contract)

def reqHeadTimestamp(contract):
    global reqId
    reqId += 1
    trade_app.reqHeadTimeStamp(reqId, contract, "TRADES", 0, 1)

def symbols_pending(data_requests):
    pending_requests = [r for r in data_requests if r['status'] != 'done']
    return bool(len(pending_requests))

#####################################################################################################

def get_symbol_data(symbol):
    global data
    currentDatetime = datetime(2023,8,10) #datetime.now()
    filepath = f"{os.path.dirname(os.path.realpath(__file__))}/data/DAX-TS-TE_2023.12.25.csv"
    data = ''
    
    with open(filepath) as f:
        for line in f:
            pass #data[symbol] += line
    #print(line)
    line_segments = line.split(',')
    date_segments = line_segments[0].split('/')
    time_segments = line_segments[1].split(':')
    get_data_from = datetime(int(date_segments[2]), int(date_segments[1]), int(date_segments[0]), int(time_segments[0]), int(time_segments[1]), int(time_segments[2]))
    print('get_data_from', get_data_from)

    startDatetime = get_data_from # - timedelta(minutes=125)
    endDatetime = startDatetime + duration_td
    reqHistData(contract(symbol),endDateTime=endDatetime, duration_str=duration_str)
    ib_request.wait()
    with open(filepath, 'a') as f:
        f.write(data)
    
    """endDatetime = get_data_from + duration_td
    while endDatetime < currentDatetime:
        ib_request.clear()
        reqHistData(contract(symbol), endDateTime=endDatetime, duration_str=duration_str)
        ib_request.wait()
        print(symbol, endDatetime.strftime("%Y-%m-%d"))
        #time.sleep(1)
        endDatetime += duration_td
        with open(filepath, 'a') as f:
            f.write(data)
        data = ''
    """

def write_symbol_data(symbol):
    filepath = f"{os.path.dirname(os.path.realpath(__file__))}/data/@F{symbol}_updated.csv"
    with open(filepath, 'w') as f:
        f.write(data)


symbol_status = {
    'DAX': 'not_started'
}
one_day_in_secs = 60*60*24
duration_td = timedelta(seconds=one_day_in_secs)
duration_str = str(one_day_in_secs) + ' S'

ib_request = threading.Event()
trade_app = TradeApp()
trade_app.connect(host='127.0.0.1', port=4002, clientId=2) #port 4002 for ib gateway paper trading/7497 for TWS paper trading
con_thread = threading.Thread(target=trade_app.run)
con_thread.start()

time.sleep(2) # Give time to connect...
print()

# reqHeadTimestamp(contract("DAX"))
# ib_request.wait()

for symbol in symbol_status.keys():
    print('\nGetting', symbol, '...')
    get_symbol_data(symbol)
    write_symbol_data(symbol)
    print('  Symbol Done!')
    #print('Throttling...')
    #time.sleep(1)

trade_app.disconnect()
print('Done!')

#print('\nTHIS IS MY DATA:')
#print(data['DAX'])
