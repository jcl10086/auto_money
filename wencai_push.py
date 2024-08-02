import datetime
import math
import time

import redis
from mootdx.quotes import Quotes
import pandas as pd
import pywencai

# 初始化账号
tdx_client = Quotes.factory(market='std')
r = redis.Redis(host='192.168.1.4', port=6379, decode_responses=True)


def convert_to_code(code):
    return code.split('.')[0]


def get_codes():
    df = pywencai.get(query='涨幅>5，涨速>2，沪深主板，非st', loop=True)
    code_array = df['股票代码']
    codes = code_array.values
    return codes


if __name__ == '__main__':
    while True:
        codes = get_codes()
        for code in codes:
            r.set(code, 'sb')
            r.expire(code, 60)
            print(code)
        time.sleep(1)