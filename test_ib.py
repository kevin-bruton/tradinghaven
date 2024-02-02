from ib_insync import *

def _positionChanged(position):
  print('Position change:', position)
  print('Num fills:', len(ib.fills()))
  print('Num trades:', len(ib.trades()))

def _executionPerformed(trade, fill):
  print('Got trade:', trade)
  print('Got fill:', fill)

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=3)
print('Initial number of fills:', len(ib.fills()))
print('Initial number of trades:', len(ib.trades()))
ib.positionEvent += _positionChanged
ib.execDetailsEvent += _executionPerformed

while True:
  ib.sleep(1)
ibTrader.disconnect()
