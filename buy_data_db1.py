# 高开买入
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
cookie = 'other_uid=Ths_iwencai_Xuangu_hg54pqsca5cpwxmxubzrnmu9gxl5bzmx; ta_random_userid=h7x5hms3yy; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=umhwFo6FJF%2FqZxPCdx%2BQaGVVO4BxcIgFcA4HC96P2H%2F18m26lRsmsSJuBvQEJCdBHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=7367FAF6251D45A88CB536A1C4018DCA; u_ttype=WEB; user_status=0; user=MDptb181NzA4OTQ0MTQ6Ok5vbmU6NTAwOjU4MDg5NDQxNDo1LDEsNDA7NiwxLDQwOzcsMTExMTExMTExMTEwLDQwOzgsMTExMTAxMTEwMDAwMTExMTEwMDEwMDEwMDEwMDAwMDAsNDA7MzMsMDAwMTAwMDAwMDAwLDEyODszNiwxMDAxMTExMTAwMDAxMTAwMTAxMTExMTEsMTI4OzQ2LDAwMDAxMTExMTAwMDAwMTExMTExMTExMSwxMjg7NTEsMTEwMDAwMDAwMDAwMDAwMCwxMjg7NTgsMDAwMDAwMDAwMDAwMDAwMDEsMTI4Ozc4LDEsMTI4Ozg3LDAwMDAwMDAwMDAwMDAwMDAwMDAxMDAwMCwxMjg7MTAzLDAwMDAwMDEwMDAwMDAwMDAsMTI4OzExNSwwMDAwMDAwMDAwMDAwMDEwMDAwMDAwMDAwMDAwMDAwMCwxMjg7MTE5LDAwMDAwMDAwMDAwMDAwMDAwMDEwMTAwMDAwMDAwMCwxMjg7MTI1LDExLDEyODs0NCwxMSw0MDsxLDEwMSw0MDsyLDEsNDA7MywxLDQwOzEwMiwxLDQwOjI0Ojo6NTcwODk0NDE0OjE3NDY1OTMxMjM6OjoxNjE1MDExMjQwOjI2Nzg0MDA6MDoxYzU4MWM0Njk4Njg0MmQwNTAwYTE2MzEyYzZiNDUyMjQ6ZGVmYXVsdF80OjE%3D; userid=570894414; u_name=mo_570894414; escapename=mo_570894414; ticket=a4f1039da2680a51c6355cc9d440a424; utk=43f2e2dbf1646ceff09a37a3fb4556c9; v=A69j3La3GzxpMB8AVAkjzpsoPsi7VAMvnagHacE9S54lEMG2ySSTxq14l6DS'

def get_codes():
    df = pywencai.get(query='5月9日未涨停，5月12日未涨停，开盘涨跌幅>2且<8，流值<300亿，沪深主板,非st，股价>3且<30', loop=True, sort_order='desc', sort_key='最新涨跌幅', cookie=cookie)
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
    # my_df = my_df[(my_df['reversed_bytes9'] >= 2) & (my_df['price'] == my_df['zt_price']) & (my_df['ask_vol1'] < 5000)]
    my_df = my_df[(my_df['reversed_bytes9'] >= 1.5) & (my_df['zf'] > 9)]
    data = my_df.nlargest(1, 'reversed_bytes9')
    return data


# 获取持仓
def buy(data):
    code = data['code'].values[0]
    # 涨停买入
    price = data['zt_price']
    enable_balance = 90000
    buy_info_zt(code, float(price), enable_balance)


def buy_info_zt(code, price, enable_balance):
    # 挂单股价
    gd_price = price
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 100) * 100
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f'当前时间：{formatted_time}  代码：{code}  挂单价格：{gd_price}  挂单数量：{gd_num}')
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
