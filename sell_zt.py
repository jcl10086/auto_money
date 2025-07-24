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
    stock_list = ['002266']
    gd_price = 4.42
    enable_amount = 7300
    # 封单阀值
    fd_num = 120000
    while True:
        # 获取当前时间
        now = datetime.now().time()
        # 设定一个指定的时间点，比如 14:30
        target_time = datetime.strptime("17:55", "%H:%M").time()
        # 判断当前时间是否大于指定时间
        if now >= target_time:
            print(f'时间：{now} ================================ 超出时间范围')
            break
        fd = get_info(stock_list)
        if fd < fd_num:
            sell(stock_list[0], gd_price, enable_amount)
            break
        time.sleep(0.5)