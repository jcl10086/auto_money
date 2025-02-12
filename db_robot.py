import math
import time
from datetime import datetime

import pandas as pd
import pywencai
from mootdx.quotes import Quotes

import easytrader
from basic import buy_info

# 打打板机器人
tdx_client = Quotes.factory(market='std')
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')


def get_codes():
    df = pywencai.get(query='涨幅>7，股价>2，昨日未涨停，沪深主板非st，今日未涨停', loop=True, sort_order='desc', sort_key='最新涨跌幅')
    codes = df['code'].values.tolist()
    return codes


def get_data(stock_list):
    # stock_list = stock_list[0:1]
    my_df = None
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)
    my_df['zf'] = (my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100
    my_df = my_df[(my_df['reversed_bytes9'] >= 4) & (my_df['zf'] >= 9)]
    # my_df['zf'] = (my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100
    # my_df = my_df[(my_df['zf'] >= 9.9)]
    data = my_df.nlargest(1, 'reversed_bytes9')
    return data


# 获取持仓
def buy(data):
    code = data['code']
    # 涨停买入
    price = data['high']
    enable_balance = 70000
    buy_info(code, float(price), enable_balance)


def position_info():
    positions = user.position
    return positions


# 获取持仓
def job():
    codes = get_codes()
    i = 0
    while True:
        if i >= 30:
            break
        i = i + 1
        print(f'=====================执行第{str(i)}次')
        data = get_data(codes)
        if len(data) == 0:
            print('====无数据====')
            time.sleep(0.5)
            continue
        code = data['code'].values[0]
        positions = position_info()
        buy_flag = False
        for position in positions:
            if code == position.stock_code:
                buy_flag = True
                continue
        if buy_flag is True:
            print(f'{code}====已买入====')
            time.sleep(0.5)
            continue
        buy(data)
        time.sleep(5)


if __name__ == '__main__':
    while True:
        job()
