import time
from datetime import datetime

import pandas as pd
import requests
from mootdx.quotes import Quotes

import easytrader



tdx_client = Quotes.factory(market='std')
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')


def get_info(code):
    url = f"http://121.43.57.182:21936/sql?token=fb6d25972a7bb566a74cf69c853e5d74&mode=level_queue&code={code}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    rs_json = response.json()
    fd = rs_json['data']['list'][0]['volume_count']
    current_time = datetime.now()
    ts = current_time.strftime('%H:%M:%S.%f')[:-3]
    print(f'时间：{ts} ================================ 封单：{fd}')
    return fd


def sell(code, gd_price, enable_amount):
    user.sell(code, price=gd_price, amount=enable_amount)


if __name__ == '__main__':
    code = ['003007']
    gd_price = 43.3
    enable_amount = 700
    # 封单阀值
    fd_num = 20000
    while True:
        # 获取当前时间
        now = datetime.now().time()
        # 设定一个指定的时间点，比如 14:30
        # target_time = datetime.strptime("14:55", "%H:%M").time()
        # # 判断当前时间是否大于指定时间
        # if now >= target_time:
        #     print(f'时间：{now} ================================ 超出时间范围')
        #     break
        fd = get_info(code[0])
        if fd < fd_num:
            sell(code[0], gd_price, enable_amount)
            break
        # time.sleep(0.5)