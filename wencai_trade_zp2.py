import math
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from mootdx.quotes import Quotes
import pandas as pd
import pywencai
import easytrader

# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')
tdx_client = Quotes.factory(market='std')


def get_codes():
    df = pywencai.get(query='开盘涨跌幅>1且<=2.5，流值小于50亿，股价>2且<18,沪深主板，非st，昨日非涨停', loop=True, sort_order='desc', sort_key='最新涨跌幅')
    codes = df['code'].values.tolist()
    return codes


def convert_to_code(code):
    return code.split('.')[0]


def get_data(stock_list):
    # stock_list = stock_list[0:1]
    my_df = None
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)
    # 过滤条件：reversed_bytes9
    my_df = my_df[(my_df['reversed_bytes9'] >= 2) & (my_df['reversed_bytes9'] <= 4)]
    my_df = my_df.sort_values(by='code', key=lambda x: x.apply(
        lambda y: (0 if y.startswith('00') else 1 if y.startswith('60') else 2 if y.startswith('30') else 3)))

    data = my_df.head(1)
    return data


def buy_info(code, price, enable_balance, name):
    # 挂单股价
    gd_price = price * 1.01
    gd_price = round(gd_price, 2)
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 100) * 100
    print(f'挂单价格：{gd_price}  挂单数量：{gd_num} {name} {code}')
    # 买入
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


def job():
    codes = get_codes()
    while True:
        data = get_data(codes)
        if len(data) == 0:
            print('====执行2====')
            continue
        code = data['code']
        price = data['price']
        name = ''
        enable_balance = 50400
        buy_info(code, float(price), enable_balance, name)
        time.sleep(0.5)


if __name__ == '__main__':
    job()