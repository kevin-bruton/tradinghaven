import requests
from .config import get_config_value

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
