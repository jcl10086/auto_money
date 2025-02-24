import math
import time
from datetime import datetime

import pandas as pd
import pywencai
from mootdx.quotes import Quotes

import easytrader
from basic import buy_info

tdx_client = Quotes.factory(market='std')
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')


def get_codes():
    df = pywencai.get(query='开盘涨幅>8，沪深主板非st，昨日连板次数<3', loop=True, sort_order='desc', sort_key='最新涨跌幅')
    codes = df['code'].values.tolist()
    return codes


def get_data(stock_list):
    my_df = None
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)

    # 涨幅
    my_df['zf'] = (my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100
    my_df['zt_price'] = round(my_df['last_close'] * 1.1, 2)
    my_df = my_df[(my_df['reversed_bytes9'] >= 1) & (my_df['price'] == my_df['zt_price']) & (my_df['ask_vol1'] < 3000)]
    data = my_df.nlargest(1, 'reversed_bytes9')
    return data


# 获取持仓
def buy(data):
    code = data['code'].values[0]
    # 涨停买入
    price = data['high']
    enable_balance = 100000
    buy_info_zt(code, float(price), enable_balance)


def buy_info_zt(code, price, enable_balance):
    # 挂单股价
    gd_price = price
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 100) * 100
    print(f'{code}  挂单价格：{gd_price}  挂单数量：{gd_num}')
    # 买入
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


def position_info():
    positions = user.position
    # positions_new = []
    # for position in positions:
    #     if position.enable_amount > 0:
    #         positions_new.append(position)
    #         break
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
        # code = data['code'].values[0]
        # positions = position_info()
        # buy_flag = False
        # for position in positions:
        #     if code == position.stock_code:
        #         buy_flag = True
        #         continue
        # if buy_flag is True:
        #     print(f'{code}====已买入====')
        #     time.sleep(0.5)
        #     continue
        buy(data)
        break


if __name__ == '__main__':
    job()
