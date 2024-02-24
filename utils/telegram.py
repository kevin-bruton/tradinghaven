import requests
from .config import get_config_value

def send_position_message(position):
  def pos_get(key):
    return position[key] if key in position else 'N/A'
  enabled = get_config_value('send_position_messages')
  if enabled:
    message = f"""Position change:  
    Strategy: {pos_get('strategyName')}  
    Broker Profile: {pos_get('brokerProfile')}  
    ExecTime: {pos_get('execTime')}  
    Symbol: {pos_get('symbol')}  
    Qty: {pos_get('execQty')}  
    Commission: {pos_get('commission')}  
    Realized P/L: {pos_get('realizedPnl')}    
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
    try:
      response = requests.post(url=url,data=data).json()
    except Exception as e:
      print('Exception sending telegram message:', repr(e))
    if 'error_code' in response:
      print('Error sending msg:', text)
      print('  ', response['description'])
    return response['ok']
