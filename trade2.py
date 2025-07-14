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
cookie = 'other_uid=Ths_iwencai_Xuangu_hg54pqsca5cpwxmxubzrnmu9gxl5bzmx; ta_random_userid=h7x5hms3yy; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=umhwFo6FJF%2FqZxPCdx%2BQaGVVO4BxcIgFcA4HC96P2H%2F18m26lRsmsSJuBvQEJCdBHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=7367FAF6251D45A88CB536A1C4018DCA; u_ttype=WEB; user_status=0; user=MDptb181NzA4OTQ0MTQ6Ok5vbmU6NTAwOjU4MDg5NDQxNDo1LDEsNDA7NiwxLDQwOzcsMTExMTExMTExMTEwLDQwOzgsMTExMTAxMTEwMDAwMTExMTEwMDEwMDEwMDEwMDAwMDAsNDA7MzMsMDAwMTAwMDAwMDAwLDEyODszNiwxMDAxMTExMTAwMDAxMTAwMTAxMTExMTEsMTI4OzQ2LDAwMDAxMTExMTAwMDAwMTExMTExMTExMSwxMjg7NTEsMTEwMDAwMDAwMDAwMDAwMCwxMjg7NTgsMDAwMDAwMDAwMDAwMDAwMDEsMTI4Ozc4LDEsMTI4Ozg3LDAwMDAwMDAwMDAwMDAwMDAwMDAxMDAwMCwxMjg7MTAzLDAwMDAwMDEwMDAwMDAwMDAsMTI4OzExNSwwMDAwMDAwMDAwMDAwMDEwMDAwMDAwMDAwMDAwMDAwMCwxMjg7MTE5LDAwMDAwMDAwMDAwMDAwMDAwMDEwMTAwMDAwMDAwMCwxMjg7MTI1LDExLDEyODs0NCwxMSw0MDsxLDEwMSw0MDsyLDEsNDA7MywxLDQwOzEwMiwxLDQwOjI0Ojo6NTcwODk0NDE0OjE3NDY1OTMxMjM6OjoxNjE1MDExMjQwOjI2Nzg0MDA6MDoxYzU4MWM0Njk4Njg0MmQwNTAwYTE2MzEyYzZiNDUyMjQ6ZGVmYXVsdF80OjE%3D; userid=570894414; u_name=mo_570894414; escapename=mo_570894414; ticket=a4f1039da2680a51c6355cc9d440a424; utk=43f2e2dbf1646ceff09a37a3fb4556c9; v=A69j3La3GzxpMB8AVAkjzpsoPsi7VAMvnagHacE9S54lEMG2ySSTxq14l6DS'


def get_codes():
    df = pywencai.get(query='昨日涨跌幅<-3，开盘涨幅>=0，9点25价格>9点24价格，非京市，非st，非科创板，非创业板', loop=True, sort_order='desc', sort_key='最新涨跌幅', pro=True, cookie=cookie)
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
    my_df = my_df[(my_df['reversed_bytes9'] >= 1)]
    # my_df = my_df[(my_df['min_zf'] >= -2) & (my_df['max_zf'] <= 7)]
    data = my_df.nlargest(1, 'reversed_bytes9')
    return data


def buy_info(code, price, enable_balance, name, zt_price):
    # 挂单股价
    gd_price = price * 1.01
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
    price = data['price']
    name = ''
    # enable_balance = 190000
    # enable_balance = get_balance()
    enable_balance = 70000
    rs = buy_info(code, float(price), enable_balance, name, zt_price)
    return rs


# 获取可用资金
def get_balance():
    balance = user.balance[0]
    # 可用资金  预留300
    enable_balance = balance.enable_balance
    return enable_balance


if __name__ == '__main__':
    codes = get_codes()
    print(f'=====共有{len(codes)}只股票=====')
    while True:
        # 获取数据
        data = get_data(codes)
        # 如果数据为空，打印信息并继续
        if len(data) == 0:
            time.sleep(0.5)
            print(f'====执行====')
            continue
        # 执行买入操作
        buy(data)