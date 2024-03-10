from ib_insync import Contract

def contract(symbol):
    if symbol == 'DAX':
        return Contract(conId=540729519, symbol='DAX', exchange='EUREX', currency='EUR')

""" from ibapi.contract import Contract

def contract(symbol):
    if symbol == 'DAX':
        contract = Contract()
        contract.conId = 540729519
        contract.symbol = "DAX"
        contract.secType = "CONTFUT"
        contract.currency = "EUR"
        contract.exchange = "EUREX"
        return contract """