# 主要作用为计算某只股票的 RSI，到达预期值时通过 qq 或者 mac 推送消息提醒你

import time
import talib
import pync
import pandas as pd
import numpy as np
import requests, json
import sys, getopt
import os
from futu import *

# 股票代码，默认 HK.999010，可通过命令参数修改
ticker = 'HK.999010'
# K线类型，默认5分图
ktype = SubType.K_5M
# 5分图
time_sharing = 5
# 接受提醒的QQ号，可通过命令参数设置
qq = ''

# 处理函数之间逻辑的变量
min = -1
notify_time = 0

# 存放各个时段的收盘价
close = []

def send_qq_message (message):
  url = 'http://127.0.0.1:8082/send_private_msg'
  data = {'user_id': qq, 'message': message}
  requests.post(url, data)

def send_mac_notify (title, content):
  pync.notify(content, title=title)

def get_history_close (get_cur_kline, ktype=SubType.K_5M, nums=60):
  global close
  ret, df = get_cur_kline(ticker, nums, ktype, AuType.QFQ)
  close = [float(x) for x in df['close']]
  print('get_history_close:', close)

def update_history_close (new_close):
  global close
  global min
  
  cur_min = time.localtime().tm_min

  if cur_min % time_sharing == 0 and min < cur_min:
    min = cur_min
    close.pop(0)
    print(new_close)
  else:
    close.pop()

  close.append(new_close)

  # print('update_history_close:', new_close)

def get_rsi (close, timeperiod=6):
  return talib.RSI(np.array(close), timeperiod)

class CurKline(CurKlineHandlerBase):
  def on_recv_rsp(self, rsp_str):
    global notify_time

    ret_code, data = super(CurKline,self).on_recv_rsp(rsp_str)
    
    if ret_code != RET_OK:
      print("CurKline: error, msg: %s" % data)
      return RET_ERROR, data

    if len(close) > 1:
      cur_close = data['close'][0]

      update_history_close(cur_close)

      rsi = get_rsi(close)[-1]

      if rsi > 70 or rsi < 30:
        local_time = time.localtime()
        cur_min = local_time.tm_min

        if notify_time < cur_min:
          notify_time = cur_min

          content = 'RSI: %d | CLOSE: %s' % (rsi, cur_close)

          send_mac_notify(time.strftime("%Y-%m-%d %H:%M:%S", local_time), content)
          send_qq_message(content)

      # print(rsi, cur_close)

    return RET_OK, data

def restart_program():
  python = sys.executable
  os.execl(python, python, * sys.argv)

def initOptions (argv):
  global qq, ticker

  helpMsg = 'RSI.py -qq <qq number> -ticker <ticker number>'

  try:
    opts, args = getopt.getopt(argv, "-h-q:-t:",["help", "qq=","ticker="])
  except getopt.GetoptError:
    print(helpMsg)
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
        print(helpMsg)
        sys.exit()
    elif opt in ("-q", "--qq"):
        qq = arg
    elif opt in ("-t", "--ticker"):
        ticker = arg

def main (argv):

  initOptions(argv)

  print('qq:', qq, 'ticker:', ticker)

  quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

  handler = CurKline()

  quote_ctx.set_handler(handler)
  quote_ctx.subscribe([ticker], [ktype])

  get_history_close(quote_ctx.get_cur_kline, ktype)

  # quote_ctx.close()

if __name__ == '__main__':
  main(sys.argv[1:])
  time.sleep(600)
  restart_program()
