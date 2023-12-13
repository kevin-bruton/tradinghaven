from utils.config import load_config
from utils.telegram import send_message

if __name__ == "__main__":
  # test message send
  load_config('c:/Users/CFD/trading-haven/')
  send_message('Hi')