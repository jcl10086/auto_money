import json
import time

from basic import *


def buy_data():
    info = {}
    positions = position_info()
    if len(positions) > 0:
        # 获取最新买入成交信息
        deal = current_deal_info()
        code = deal['stock_code']
        enable_amount = deal['deal_amount']
        cb_price = deal['deal_price']
        flag = sell_strategy(code, cb_price, enable_amount)
        if flag:
            info = f'{code} 卖出'
        return info

    df = get_speed(codes)
    for index, row in df.iterrows():
        code = row['code']
        if not get_last_trade(code):
            break
        enable_balance = get_balance()
        balance = enable_balance
        last_trade = get_last_trade(code)
        if last_trade:
            price = row['price']
            # balance = 10000
            buy_info(code, price, balance)
            break


if __name__ == '__main__':
    codes = get_codes()
    while True:
        info = buy_data()
        print(info)
        time.sleep(1)