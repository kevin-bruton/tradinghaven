
# read file 'exported_titan.txt' to string
#titan_results = open('exported_titan.txt', 'r').read()
#print('TITAN CONFIG:')
#print(titan_results)
#
#strategies_per_workspace = 6

class Chart:
  def __init__(self, timeframe, symbol, data_feed, symbol_desc, exchange):
    self.timeframe = timeframe
    self.symbol = symbol
    self.data_feed = data_feed
    self.symbol_desc = symbol_desc
    self.exchange = exchange

class Strategy:
  def __init__(self, name, profile, contracts, charts=[]):
    self.name = name
    self.profile = profile
    self.contracts = contracts
    self.charts = charts
    if len(charts) > 0:
      self.symbol_name = charts[0].symbol + ' - ' + charts[0].timeframe + ' Minutes - ' + charts[0].data_feed

account = 'DU3220378'
data_feed = 'TradeStation'
strategies = [
  Strategy(
    name='TOP_UA_666_GC_5',
    profile='Interactive Brokers',
    contracts=5,
    charts=[
      Chart(
        symbol='@GC',
        timeframe='5', 
        data_feed='TradeStation',
        symbol_desc='Gold Continuous Contract [Feb25]',
        exchange='COMEX'
      )
    ]
  ),
]

workspace = open('WspStart.txt', 'r').read()

for strat_idx, strategy  in enumerate(strategies):
  window_num = str(strat_idx)
  
  window_start = open('WspWindowGeneric.txt', 'r').read()
  window_end = open('WspWindowGeneric2.txt', 'r').read()
  charts = ''

  for chart_idx, chart in enumerate(strategy.charts):
    chart_str = open('WspChart.txt', 'r').read()
    chart_str = chart_str \
      .replace('%Chart_Num%', 'Chart_' + str(chart_idx)) \
      .replace('%Data_Feed%', chart.data_feed) \
      .replace('%Symbol_Desc%', chart.symbol_desc) \
      .replace('%Exchange%', chart.exchange) \
      .replace('%Symbol%', chart.symbol) \
      .replace('%Timeframe%', chart.timeframe)
    charts += chart_str

  window = (window_start + charts + window_end) \
    .replace('%Window_Num%', 'Window_' + str(window_num)) \
    .replace('%Profile%', strategy.profile) \
    .replace('%Strategy_Name%', strategy.name) \
    .replace('%Symbol_Name%', strategy.symbol_name) \
    .replace('%Account%', account) \
    .replace('%Num_Contracts%', str(strategy.contracts))
  workspace += window

# Save the new workspace
workspace_path = 'Live_Trading.wsp'
with open(workspace_path, 'w') as f:
  f.write(workspace)

