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
    df = pywencai.get(query='涨幅>1，沪深主板非st，股价>2，流值<100亿，卖一>0，昨日未涨停', loop=True, sort_order='desc', sort_key='最新涨跌幅')
    codes = df['code'].values.tolist()
    return codes


def get_data(stock_list):
    # stock_list = stock_list[0:1]
    my_df = None
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)
    # 涨幅
    # my_df['zf'] = (my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100
    # my_df = my_df[(my_df['reversed_bytes9'] >= 4) & (my_df['zf'] >= 9)]
    # my_df['zt_price'] = round(my_df['last_close'] * 1.1, 2)
    # my_df['zf'] = (my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100
    # my_df = my_df[(my_df['reversed_bytes9'] > 2) & (my_df['zf'] > 8)]
    # my_df['zt_price'] = round(my_df['last_close'] * 1.1, 2)
    # 过滤条件：reversed_bytes9
    # my_df = my_df[(my_df['price'] == my_df['zt_price']) & (my_df['price'] == my_df['bid1']) & (my_df['bid_vol1'] < 50000)]
    # my_df = my_df[(my_df['reversed_bytes9'] >= 1) & (my_df['zf'] >= 9.5)]
    # data = my_df.nlargest(1, 'reversed_bytes9')

    # 涨幅
    my_df['zf'] = (my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100
    my_df['zt_price'] = round(my_df['last_close'] * 1.1, 2)
    my_df = my_df[(my_df['reversed_bytes9'] >= 2) & (my_df['price'] == my_df['zt_price']) & (my_df['ask_vol1'] < 15000)]
    data = my_df.nlargest(1, 'reversed_bytes9')
    return data


# 获取持仓
def buy(data):
    code = data['code'].values[0]
    # 涨停买入
    price = data['zt_price']
    enable_balance = 85700
    buy_info(code, float(price), enable_balance)


def buy_info(code, price, enable_balance):
    # 挂单股价
    gd_price = price
    # gd_price = round(gd_price, 2)
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 100) * 100
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f'当前时间：{formatted_time}  代码：{code}  挂单价格：{gd_price}  挂单数量：{gd_num}')
    # 买入
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


def position_info():
    positions = user.position
    return positions


# 获取持仓
def job():
    codes = get_codes()
    while True:
        data = get_data(codes)
        if len(data) == 0:
            print('====无数据====')
            time.sleep(0.5)
            continue
        buy(data)
        break


if __name__ == '__main__':
    job()
