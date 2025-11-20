#!python3
# -*- coding:utf-8 -*-
# 依赖安装: pip install websocket-client
# level10 涨停板卖出
# 正常价格卖出
import time
from datetime import datetime

import pandas as pd
import requests
import websocket
import zlib
import easytrader
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')
wsUrl = ''
max_price = 0


def get_wsurl():
    url = "http://jvQuant.com/query/server?market=ab&type=websocket&token=fb6d25972a7bb566a74cf69c853e5d74"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    wsUrl = response.json()['server'] + '/?token=fb6d25972a7bb566a74cf69c853e5d74'
    return wsUrl


def trade_data(results):
    flag = False
    df = pd.DataFrame(results)
    current_time = datetime.now()
    ts = current_time.strftime('%H:%M:%S.%f')[:-3]
    df['ts'] = ts
    print(df)
    if results[0]['buy1_qty']  < 10000000:
        gd_price = round(zt_price * 0.985, 2)
        # 执行卖出入操作
        sell(code, gd_price, enable_amount)
        flag = True
    return flag

def sell(code, gd_price, enable_amount):
    user.sell(code, price=gd_price, amount=enable_amount)

# 发送订阅
def on_open(ws):
    ws.send("all=lv10_" + code[0])


# 接收推送
def on_message(ws, message, type, flag):
    # 命令返回文本消息
    if type == websocket.ABNF.OPCODE_TEXT:
        print(time.strftime('%H:%M:%S', time.localtime(time.time())), "Text响应:", message)
    # 行情推送压缩二进制消息，在此解压缩
    if type == websocket.ABNF.OPCODE_BINARY:
        rb = zlib.decompress(message, -zlib.MAX_WBITS)
        results = parse_level10_data(rb.decode("utf-8"))
        if trade_data(results):
            exit()


def on_error(ws, error):
    print(error)


def on_close(ws, code, msg):
    print(time.strftime('%H:%M:%S', time.localtime(time.time())), "连接已断开")


def get_buy1_quantity(data_str):
    parts = data_str.split(',')

    # 找到买十档数量开始位置
    # 数据格式：时间,名称,最新价,昨收,成交额,成交量,买十价格(10个),买十数量(10个),卖十价格(10个),卖十数量(10个)
    buy_prices_start = 6
    buy_quantities_start = buy_prices_start + 10  # 买十档数量开始位置

    if len(parts) >= buy_quantities_start + 10:
        buy1_quantity = int(parts[buy_quantities_start])
        return buy1_quantity
    else:
        return None


def parse_level10_data(data):
    global max_price
    results = []
    for line in data.strip().split('\n'):
        key, value = line.split('=')
        code = key.replace('lv10_', '')
        buy1_qty = get_buy1_quantity(value)

        result ={
            'code': code,
            'buy1_qty': buy1_qty
        }
        results.append(result)
    return results


wsUrl = get_wsurl()
# wsUrl = "ws://114.55.97.180:21966/?token=fb6d25972a7bb566a74cf69c853e5d74"
#分配服务器方法请参考：jvQuant.com/wiki/开始使用/分配服务器.html

ws = websocket.WebSocketApp(wsUrl,
                            on_open=on_open,
                            on_data=on_message,
                            on_error=on_error,
                            on_close=on_close)




if __name__ == '__main__':
    code = ['600477']
    enable_amount = 29200
    # 涨停价
    zt_price = 3.1
    ws.run_forever()
