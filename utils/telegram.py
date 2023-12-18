import requests
from .config import get_config_value

def send_position_message(position):
  def pos_get(key):
    return position[key] if key in position else 'N/A'
  enabled = get_config_value('send_position_messages')
  if enabled:
    message = f"""Position change:  
    Strategy: {pos_get('strategy_name')}  
    Order name: {pos_get('order_name')}  
    Account: {pos_get('account')}  
    Symbol: {pos_get('symbol')} {pos_get('contract')}  
    Qty: {pos_get('qty')}  
    Price: {pos_get('price')}  
    Generated: {pos_get('generated')}    
    Final: {pos_get('final')}    
    Action: {pos_get('action')}    
    Order Type: {pos_get('order_type')}    
    State: {pos_get('state')}    
    Fill Qty: {pos_get('fill_qty')}  
    Fill Price: {pos_get('fill_price')}  
    OPL: {pos_get('opl')}  
    Realized P/L: {pos_get('realized_pl')}   
    """
    send_message(message)

def send_message(text):
  token = get_config_value('telegram_token')
  chat_id = get_config_value('telegram_chat_id')

  if token and chat_id:
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
      'chat_id': chat_id,
      'text': text,
      'parse_mode': 'HTML'
    }
    response = requests.post(url=url,data=data).json()
    if 'error_code' in response:
      print('Error sending msg:', text)
      print('  ', response['description'])
    return response['ok']
