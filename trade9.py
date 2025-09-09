#!python3
# -*- coding:utf-8 -*-
# 依赖安装: pip install websocket-client
# level2 涨速买入  逐笔成交   创业板
import math
import sys
import time
from datetime import datetime

import time

import pandas as pd
import websocket
import zlib
import pywencai
from mootdx.quotes import Quotes

import easytrader

# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')
tdx_client = Quotes.factory(market='std')
cookie = 'other_uid=Ths_iwencai_Xuangu_hg54pqsca5cpwxmxubzrnmu9gxl5bzmx; ta_random_userid=h7x5hms3yy; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=umhwFo6FJF%2FqZxPCdx%2BQaGVVO4BxcIgFcA4HC96P2H%2F18m26lRsmsSJuBvQEJCdBHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=7367FAF6251D45A88CB536A1C4018DCA; u_ttype=WEB; user_status=0; user=MDptb181NzA4OTQ0MTQ6Ok5vbmU6NTAwOjU4MDg5NDQxNDo1LDEsNDA7NiwxLDQwOzcsMTExMTExMTExMTEwLDQwOzgsMTExMTAxMTEwMDAwMTExMTEwMDEwMDEwMDEwMDAwMDAsNDA7MzMsMDAwMTAwMDAwMDAwLDEyODszNiwxMDAxMTExMTAwMDAxMTAwMTAxMTExMTEsMTI4OzQ2LDAwMDAxMTExMTAwMDAwMTExMTExMTExMSwxMjg7NTEsMTEwMDAwMDAwMDAwMDAwMCwxMjg7NTgsMDAwMDAwMDAwMDAwMDAwMDEsMTI4Ozc4LDEsMTI4Ozg3LDAwMDAwMDAwMDAwMDAwMDAwMDAxMDAwMCwxMjg7MTAzLDAwMDAwMDEwMDAwMDAwMDAsMTI4OzExNSwwMDAwMDAwMDAwMDAwMDEwMDAwMDAwMDAwMDAwMDAwMCwxMjg7MTE5LDAwMDAwMDAwMDAwMDAwMDAwMDEwMTAwMDAwMDAwMCwxMjg7MTI1LDExLDEyODs0NCwxMSw0MDsxLDEwMSw0MDsyLDEsNDA7MywxLDQwOzEwMiwxLDQwOjI0Ojo6NTcwODk0NDE0OjE3NDY1OTMxMjM6OjoxNjE1MDExMjQwOjI2Nzg0MDA6MDoxYzU4MWM0Njk4Njg0MmQwNTAwYTE2MzEyYzZiNDUyMjQ6ZGVmYXVsdF80OjE%3D; userid=570894414; u_name=mo_570894414; escapename=mo_570894414; ticket=a4f1039da2680a51c6355cc9d440a424; utk=43f2e2dbf1646ceff09a37a3fb4556c9; v=A69j3La3GzxpMB8AVAkjzpsoPsi7VAMvnagHacE9S54lEMG2ySSTxq14l6DS'
codes = []
my_df = None

def trade_data(results):
    flag = False
    df = pd.DataFrame(results)

    merged = pd.merge(df, my_df, on='code', how='inner')
    df = merged[['code', 'current_price', 'zt_price', 'open']]
    current_time = datetime.now()
    ts = current_time.strftime('%H:%M:%S.%f')[:-3]
    df['ts'] = ts
    print(df)
    df['speed'] =  (df['current_price'] - df['open']) / df['open'] * 100
    # df = df[(df['buy1_price'] == df['zt_price']) & (df['buy1_quantity'] > 5000000)]
    df = df[(df['speed'] >= 1) & (df['speed'] <= 2.5)]
    data = df.nlargest(1, 'speed')
    # 如果数据为空，打印信息并继续
    if len(data) > 0:
        # 执行买入操作
        buy(data)
        flag = True
    return flag

# 前日涨幅大于5，昨日涨跌幅小于2，创业板，9点25价格>=9点24价格，开盘涨跌幅>-2且开盘涨跌幅<2
# 股价<30且>5，创业板，非st，昨日未涨停，9点25价格>=9点24价格，开盘涨跌幅>-2且开盘涨跌幅<2
def get_codes():
    global codes
    df = pywencai.get(query='股价<30且>5，创业板，非st，昨日未涨停，9点25价格>=9点24价格，开盘涨跌幅>-2且开盘涨跌幅<2', loop=True, sort_order='desc', sort_key='最新涨跌幅', pro=True, cookie=cookie)
    codes = df['code'].values.tolist()

    # 移除数组
    # codes_remove = ['002238']
    # codes = [x for x in codes if x not in codes_remove]

    # 指定股票
    # codes = ['000514']
    return codes


def get_data(stock_list):
    # stock_list = stock_list[0:1]
    global my_df
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)

    my_df['zt_price'] = round(my_df['last_close'] * 1.2, 2)
    # my_df = my_df[(my_df['min_zf'] >= -2) & (my_df['max_zf'] <= 7)]
    # data = my_df.nsmallest(1, 'price')
    return my_df


# 发送订阅
def on_open(ws):
    # 用列表推导式和 join 拼接
    all_codes = "all=" + ",".join([f"lv2_{code}" for code in codes])
    ws.send(all_codes)


# 接收推送
def on_message(ws, message, type, flag):
    # 命令返回文本消息
    if type == websocket.ABNF.OPCODE_TEXT:
        print(time.strftime('%H:%M:%S', time.localtime(time.time())), "Text响应:", message)
    # 行情推送压缩二进制消息，在此解压缩
    if type == websocket.ABNF.OPCODE_BINARY:
        rb = zlib.decompress(message, -zlib.MAX_WBITS)
        # print(time.strftime('%H:%M:%S', time.localtime(time.time())), "Binary响应:", rb.decode("utf-8"))
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


wsUrl = "ws://114.55.97.180:21966/?token=fb6d25972a7bb566a74cf69c853e5d74"
#分配服务器方法请参考：jvQuant.com/wiki/开始使用/分配服务器.html

ws = websocket.WebSocketApp(wsUrl,
                            on_open=on_open,
                            on_data=on_message,
                            on_error=on_error,
                            on_close=on_close)


def buy_info(code, price, enable_balance, name, zt_price):
    # 挂单股价
    gd_price = price * 1.005
    gd_price = round(gd_price, 2)
    if gd_price >= zt_price:
        gd_price = zt_price
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 100) * 100
    print(f'挂单价格：{gd_price}  挂单数量：{gd_num} {name} {code}')
    # 买入
    rs = user.buy(code, price=gd_price, amount=gd_num)
    return rs


def buy(data):
    zt_price = data['zt_price'].values[0]
    code = data['code']
    price = data['current_price']
    name = ''
    # enable_balance = 190000
    # enable_balance = get_balance()
    enable_balance = 46400
    try:
        rs = buy_info(code, float(price), enable_balance, name, zt_price)
    except Exception as e:
        print(e)
        exit()
    return rs


# 获取可用资金
def get_balance():
    balance = user.balance[0]
    # 可用资金  预留300
    enable_balance = balance.enable_balance
    return enable_balance


if __name__ == '__main__':
    while True:
        # 获取当前时间
        now = datetime.now().time()
        # 设定一个指定的时间点，比如 14:30
        target_time = datetime.strptime("09:30:30", "%H:%M:%S").time()
        # 判断当前时间是否大于指定时间
        if now >= target_time:
            break
        time.sleep(5)

    codes = get_codes()
    my_df = get_data(codes)
    print(f'=====共有{len(codes)}只股票=====')
    ws.run_forever()
    # while True:
    #     ws.run_forever()
    #     # 获取数据
    #     # data = get_data(codes)
    #     # 如果数据为空，打印信息并继续
    #     if len(data) == 0:
    #         time.sleep(0.5)
    #         print(f'====执行====')
    #         continue
    #     # 执行买入操作
    #     buy(data)
    #     break