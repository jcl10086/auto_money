import datetime
import math
import time
from mootdx.quotes import Quotes
import pandas as pd
import pywencai

import easytrader

# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')
tdx_client = Quotes.factory(market='std')


def get_codes():
    df = pywencai.get(query='开盘涨跌幅大于-1.5小于2，流值小于30亿，股价>4,沪深主板，非st，昨日非涨停', loop=True, sort_order='desc', sort_key='最新涨跌幅')
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
        my_df = my_df[(my_df['reversed_bytes9'] >= 3) & (my_df['reversed_bytes9'] <= 4)]
    # 过滤竞价涨幅
    # my_df['jj_zf'] = round((my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100, 2)
    # my_df = my_df[(my_df['jj_zf'] >= -2) & (my_df['jj_zf'] <= 2.5)]
    my_df = my_df[(my_df['cur_vol'] >= 1000)]
    # 按照Score列进行降序排序，并获取Top 1行
    data = my_df.nlargest(1, 'reversed_bytes9')
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


if __name__ == '__main__':
    codes = get_codes()
    # 获取当前时间
    now = datetime.datetime.now()
    # 将时间格式化为指定格式
    formatted_date = now.strftime("%Y%m%d")
    key = '收盘价:不复权[' + formatted_date + ']'
    while True:
        data = get_data(codes)
        if len(data) == 0:
            print('====执行====')
            continue
        code = data['code']
        price = data['price']
        name = ''
        enable_balance = 58900
        buy_info(code, float(price), enable_balance, name)
        time.sleep(1)