import time
from datetime import datetime

import pandas as pd
from mootdx.quotes import Quotes

import easytrader



tdx_client = Quotes.factory(market='std')
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')


def get_info(stock_list):
    current_time = datetime.now()
    # 格式化时间
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    my_df = None
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)
    fd = my_df['bid_vol1'].values[0]
    print(f'时间：{formatted_time} ================================ 封单：{fd}')
    return fd


def sell(code, gd_price, enable_amount):
    user.sell(code, price=gd_price, amount=enable_amount)


if __name__ == '__main__':
    stock_list = ['603109']
    gd_price = 13.35
    enable_amount = 4100
    # 封单阀值
    fd_num = 20000
    while True:
        fd = get_info(stock_list)
        if fd < fd_num:
            sell(stock_list[0], gd_price, enable_amount)
            break
        time.sleep(1)