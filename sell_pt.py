#!python3
# -*- coding:utf-8 -*-
# 依赖安装: pip install websocket-client
# level2 打板  逐笔成交
# 正常价格卖出
import time
from datetime import datetime

import pandas as pd
import websocket
import zlib
import easytrader
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')


def trade_data(results):
    flag = False
    df = pd.DataFrame(results)
    current_time = datetime.now()
    ts = current_time.strftime('%H:%M:%S.%f')[:-3]
    df['ts'] = ts
    print(df)
    if results[0]['current_price'] < compare_price:
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
        results = parse_level2_data(rb.decode("utf-8"))
        if trade_data(results):
            exit()


def on_error(ws, error):
    print(error)


def on_close(ws, code, msg):
    print(time.strftime('%H:%M:%S', time.localtime(time.time())), "连接已断开")


def parse_level2_data(data):
    results = []
    for line in data.strip().split('\n'):
        key, value = line.split('=')
        code = key.replace('lv2_', '')

        # 获取最后一笔成交数据
        last_record = value.split('|')[-1]  # 取最后一个成交记录
        fields = last_record.split(',')  # 拆分字段

        current_price = float(fields[2])  # 成交价格是第3项
        result ={
            'code': code,
            'current_price': current_price
        }
        results.append(result)
    return results


wsUrl = "ws://121.43.57.182:21967/?token=fb6d25972a7bb566a74cf69c853e5d74"
#分配服务器方法请参考：jvQuant.com/wiki/开始使用/分配服务器.html

ws = websocket.WebSocketApp(wsUrl,
                            on_open=on_open,
                            on_data=on_message,
                            on_error=on_error,
                            on_close=on_close)


if __name__ == '__main__':
    code = ['300987']
    gd_price = 20.95
    enable_amount = 1400
    compare_price = 21
    ws.run_forever()
