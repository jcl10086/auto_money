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
    df = pywencai.get(query='昨日未涨停，开盘涨幅>0且<2，沪深主板，非st，流值<100亿，股价<20', loop=True, sort_order='desc', sort_key='最新涨跌幅')
    codes = df['code'].values.tolist()
    return codes


def get_codes2():
    df = pywencai.get(query='开盘涨跌幅>=0且<5，创业板', loop=True, sort_order='desc', sort_key='最新涨跌幅')
    codes = df['code'].values.tolist()
    return codes


def get_codes3():
    df = pywencai.get(query='开盘涨跌幅>-2，创业板，昨日未涨停', loop=True, sort_order='desc', sort_key='最新涨跌幅')
    codes = df['code'].values.tolist()
    return codes


def get_codes4():
    df = pywencai.get(query='开盘涨跌幅=0，流值小于50亿，股价>1且<12,沪深主板，非st，昨日未涨停且前日未涨停', loop=True, sort_order='desc', sort_key='最新涨跌幅')
    codes = df['code'].values.tolist()
    return codes


def get_codes5():
    df = pywencai.get(query='开盘涨跌幅>0.3且<1，流值小于50亿，股价>1且<12,沪深主板，非st，昨日未涨停且前日未涨停', loop=True, sort_order='desc', sort_key='最新涨跌幅')
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

    # my_df['max_zf'] = (my_df['high'] - my_df['last_close']) / my_df['last_close'] * 100
    # my_df['min_zf'] = (my_df['low'] - my_df['last_close']) / my_df['last_close'] * 100
    # 过滤条件：reversed_bytes9
    my_df = my_df[(my_df['reversed_bytes9'] >= 3.5) & (my_df['vol'] > 2000)]
    # my_df = my_df[(my_df['min_zf'] >= -2) & (my_df['max_zf'] <= 7)]
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


def buy(data):
    code = data['code']
    price = data['price']
    name = ''
    enable_balance = 100000
    buy_info(code, float(price), enable_balance, name)


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


def job2():
    execute_job(get_codes2, "Job 2")


def job3():
    execute_job(get_codes3, "Job 3")


def job4():
    execute_job(get_codes4, "Job 4")


def job5():
    execute_job(get_codes5, "Job 5")


if __name__ == '__main__':
    print()