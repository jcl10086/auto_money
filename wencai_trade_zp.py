import math
import sys
import time
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from mootdx.quotes import Quotes
import pandas as pd
import pywencai
import easytrader
import subprocess

# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')
tdx_client = Quotes.factory(market='std')


def get_codes1():
    df = pywencai.get(query='7月3日未涨停，开盘涨幅>5且<9，沪深主板非st，股价>3', loop=True, sort_order='desc', sort_key='最新涨跌幅')
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

    my_df['zf'] = (my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100
    # my_df['om_zf'] = (my_df['open'] - my_df['low']) / my_df['low'] * 100
    # my_df['pm_zf'] = (my_df['price'] - my_df['low']) / my_df['low'] * 100
    my_df['zt_price'] = round(my_df['last_close'] * 1.1, 2)
    # 过滤条件：reversed_bytes9
    my_df = my_df[(my_df['reversed_bytes9'] >= 0) & (my_df['zf'] >= 9.5)]
    # my_df = my_df[(my_df['om_zf'] > 2) & (my_df['pm_zf'] > 2) & (my_df['zf'] < 2) & (my_df['zf'] > -4)]
    data = my_df.nlargest(1, 'reversed_bytes9')
    return data


def buy_info(code, price, enable_balance, name, zt_price):
    # 挂单股价
    # gd_price = price * 1.01
    # gd_price = round(gd_price, 2)
    gd_price = zt_price
    # if gd_price >= zt_price:
    #     gd_price = zt_price
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 100) * 100
    print(f'挂单价格：{gd_price}  挂单数量：{gd_num} {name} {code}')
    # 买入
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


def buy(data):
    # data = data.index
    code = data['code']
    price = data['price']
    zt_price = data['zt_price']
    name = ''
    enable_balance = 50000
    buy_info(code, float(price), enable_balance, name, float(zt_price))


# 通用的执行函数
def execute_job(get_codes_func, job_name):
    codes = get_codes_func()
    print(f'=====共有{len(codes)}只股票，正在执行{job_name}=====')

    while True:
        # # 获取当前时间
        # current_time = datetime.now()
        #
        # # 检查时间是否超过 9点30分30秒
        # if current_time.hour > 9 or (current_time.hour == 9 and current_time.minute > 31) or (
        #         current_time.hour == 9 and current_time.minute == 31 and current_time.second >= 10):
        # 获取数据
        data = get_data(codes)
        # 如果数据为空，打印信息并继续
        if len(data) == 0:
            print(f'===={job_name}执行====')
            continue
        # 执行买入操作
        buy(data)


# 定义具体的 job 调用函数
def job1():
    execute_job(get_codes1, "Job 1")


if __name__ == '__main__':
    print()