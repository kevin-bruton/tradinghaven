import requests
from .config import get_config_value

token = get_config_value('telegram_token')
chat_id = get_config_value('telegram_chat_id')

def sendMessage(text):
  if token and chat_id:
    response = requests.post(
            url=f'https://api.telegram.org/bot{token}/sendMessage',
            data={'chat_id': chat_id, 'text': text, 'parse_mode': 'MarkdownV2'}
        ).json()
    return response['ok']
  