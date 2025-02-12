import math

import numpy as np
import pandas as pd
from mootdx.quotes import Quotes
from scipy.stats import linregress

import easytrader
import pywencai

import pymysql

max_zf = 0
min_zf = 10000
min_count = 0
max_price = 0
min_price = 0


tdx_client = Quotes.factory(market='std')
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')


def buy_info(code, price, enable_balance):
    # 挂单股价
    gd_price = price * 1.001
    gd_price = round(gd_price, 2)
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 100) * 100
    print(f'挂单价格：{gd_price}  挂单数量：{gd_num}')
    # 买入
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


def get_speed(stock_list):
    my_df = None
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)
    # 过滤条件：reversed_bytes9
    my_df = my_df[(my_df['reversed_bytes9'] >= 0.2) & (my_df['reversed_bytes9'] <= 1)]
    # 过滤涨幅
    # my_df = my_df[(my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100 < 5]
    # 按照Score列进行降序排序，并获取Top 3行
    my_df = my_df.nlargest(1, 'reversed_bytes9')
    return my_df


def get_last_trade(code):
    flag = False
    data = tdx_client.transaction(symbol=code, start=0, offset=5)
    prices = data['price'].values
    sum_vol = sum(data['vol'].values)
    if sum_vol >= 500 and prices[4] > prices[0]:
        flag = True
    return flag


def get_codes():
    codes = []
    df = pywencai.get(query='可转债，价格>60', loop=True, sort_order='asc', query_type='conbond')
    code_array = df['可转债@可转债代码']
    for ca in code_array:
        codes.append(ca.split('.')[0])
    return codes


# 获取可用资金
def get_balance():
    balance = user.balance[0]
    # 可用资金  预留300
    enable_balance = balance.enable_balance - 300
    return enable_balance


# 获取持仓
# stock_code 代码  cost_price 成本价  enable_amount 可用数量
def position_info():
    positions = user.position
    positions_new = []
    for position in positions:
        if position.enable_amount > 0:
            positions_new.append(position)
            break
    return positions_new


def current_deal_info():
    moneys = []
    amounts = []
    stock_code = ''
    # 获取最新买入 stock_code 代码  deal_price 成本价  deal_amount 可用数量
    for deal in user.current_deal:
        if deal.bs_type == 'S':
            break
        stock_code = deal.stock_code
        deal_price = deal.deal_price
        deal_amount = deal.deal_amount
        amounts.append(deal_amount)
        money = deal_amount * deal_price
        moneys.append(money)
    deal_price = round(sum(moneys) / sum(amounts), 2)
    deal_amount = sum(amounts)
    deal_new = {}
    deal_new['deal_price'] = deal_price
    deal_new['deal_amount'] = deal_amount
    deal_new['stock_code'] = stock_code
    return deal_new


def get_price(code):
    df = tdx_client.quotes(symbol=[code])
    return df['price']


def sell(code, gd_price, enable_amount):
    user.sell(code, price=gd_price, amount=enable_amount)


def sell_strategy(code, cb_price, enable_amount):
    global min_count
    global max_zf
    global min_zf
    global max_price
    global min_price

    dq_price = round(get_price(code)[0], 2)
    zf = round((dq_price - cb_price) / cb_price * 100, 2)

    # if max_zf > 0.4 and zf < 0.1:
    #     gd_price = round(dq_price * 0.999, 2)
    #     sell(code, gd_price, enable_amount)
    #     max_zf = 0
    #     min_zf = 10000
    #     min_count = 0
    #     max_price = 0
    #     min_price = 0
    #     return True

    if zf >= max_zf:
        max_zf = zf
        min_count = 0
        min_zf = zf
        max_price = dq_price
        min_price = dq_price

    if zf < min_zf:
        min_zf = zf
        min_count = min_count + 1
        min_price = dq_price

    print(f'{code}  {zf} 成本：{cb_price} 当前：{dq_price} 最大值：{max_price} 最小值：{min_price} 计数：{min_count}')

    if min_count >= 8:
        gd_price = round(dq_price * 0.999, 2)
        sell(code, gd_price, enable_amount)
        max_zf = 0
        min_zf = 10000
        min_count = 0
        max_price = 0
        min_price = 0
        return True

    if zf <= -2:
        gd_price = round(cb_price * 0.99, 2)
        sell(code, gd_price, enable_amount)
        max_zf = 0
        min_zf = 10000
        min_count = 0
        max_price = 0
        min_price = 0
        return True
    return False
