import math
import sys
import time
from datetime import datetime

import time

import pandas as pd
import websocket
import zlib
import pywencai
import easytrader

# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')
cookie = 'other_uid=Ths_iwencai_Xuangu_hg54pqsca5cpwxmxubzrnmu9gxl5bzmx; ta_random_userid=h7x5hms3yy; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=umhwFo6FJF%2FqZxPCdx%2BQaGVVO4BxcIgFcA4HC96P2H%2F18m26lRsmsSJuBvQEJCdBHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=7367FAF6251D45A88CB536A1C4018DCA; u_ttype=WEB; user_status=0; user=MDptb181NzA4OTQ0MTQ6Ok5vbmU6NTAwOjU4MDg5NDQxNDo1LDEsNDA7NiwxLDQwOzcsMTExMTExMTExMTEwLDQwOzgsMTExMTAxMTEwMDAwMTExMTEwMDEwMDEwMDEwMDAwMDAsNDA7MzMsMDAwMTAwMDAwMDAwLDEyODszNiwxMDAxMTExMTAwMDAxMTAwMTAxMTExMTEsMTI4OzQ2LDAwMDAxMTExMTAwMDAwMTExMTExMTExMSwxMjg7NTEsMTEwMDAwMDAwMDAwMDAwMCwxMjg7NTgsMDAwMDAwMDAwMDAwMDAwMDEsMTI4Ozc4LDEsMTI4Ozg3LDAwMDAwMDAwMDAwMDAwMDAwMDAxMDAwMCwxMjg7MTAzLDAwMDAwMDEwMDAwMDAwMDAsMTI4OzExNSwwMDAwMDAwMDAwMDAwMDEwMDAwMDAwMDAwMDAwMDAwMCwxMjg7MTE5LDAwMDAwMDAwMDAwMDAwMDAwMDEwMTAwMDAwMDAwMCwxMjg7MTI1LDExLDEyODs0NCwxMSw0MDsxLDEwMSw0MDsyLDEsNDA7MywxLDQwOzEwMiwxLDQwOjI0Ojo6NTcwODk0NDE0OjE3NDY1OTMxMjM6OjoxNjE1MDExMjQwOjI2Nzg0MDA6MDoxYzU4MWM0Njk4Njg0MmQwNTAwYTE2MzEyYzZiNDUyMjQ6ZGVmYXVsdF80OjE%3D; userid=570894414; u_name=mo_570894414; escapename=mo_570894414; ticket=a4f1039da2680a51c6355cc9d440a424; utk=43f2e2dbf1646ceff09a37a3fb4556c9; v=A69j3La3GzxpMB8AVAkjzpsoPsi7VAMvnagHacE9S54lEMG2ySSTxq14l6DS'
codes = []

def trade_data(results):
    flag = False
    df = pd.DataFrame(results)
    print(df)
    df = df[(df['buy1_price'] == df['zt_price']) & (df['buy1_quantity'] > 5000000)]
    data = df.nsmallest(1, 'zt_price')
    # 如果数据为空，打印信息并继续
    if len(data) == 0:
        print(f'====执行====')
    else:
        # 执行买入操作
        buy(data)
        flag = True
    return flag

def get_codes():
    global codes
    df = pywencai.get(query='开盘涨跌幅>7，开盘未涨停，昨日非连板，非京市，非st，非科创板，非创业板', loop=True, sort_order='desc', sort_key='最新涨跌幅', pro=True, cookie=cookie)
    codes = df['code'].values.tolist()

    # 移除数组
    # codes_remove = ['002238']
    # codes = [x for x in codes if x not in codes_remove]

    # 指定股票
    # codes = ['000514']
    return codes


# 发送订阅
def on_open(ws):
    # 用列表推导式和 join 拼接
    all_codes = "all=" + ",".join([f"lv10_{code}" for code in codes])
    ws.send(all_codes)


# 接收推送
def on_message(ws, message, type, flag):
    # 命令返回文本消息
    if type == websocket.ABNF.OPCODE_TEXT:
        print(time.strftime('%H:%M:%S', time.localtime(time.time())), "Text响应:", message)
    # 行情推送压缩二进制消息，在此解压缩
    if type == websocket.ABNF.OPCODE_BINARY:
        rb = zlib.decompress(message, -zlib.MAX_WBITS)
        # print(time.strftime('%H:%M:%S', time.localtime(time.time())), "Binary响应:", rb.decode("utf-8"))
        results = parse_level10_data(rb.decode("utf-8"))
        if trade_data(results):
            exit()


def on_error(ws, error):
    print(error)


def on_close(ws, code, msg):
    print(time.strftime('%H:%M:%S', time.localtime(time.time())), "连接已断开")


def parse_level10_data(data):
    results = []
    for line in data.strip().split('\n'):
        if not line.startswith('lv10_'):
            continue
        # 分割证券代码和行情数据
        code_part, values = line.split('=', 1)
        code = code_part.replace('lv10_', '')
        # 分割各字段数据
        fields = values.split(',')
        # 提取关键数据
        prev_close = float(fields[3])  # 昨收价
        # 买一价格（买十档的第一个价格）
        buy1_price = float(fields[6])
        # 买一数量（买十档的第一个数量，位于买十档价格后的第10个位置）
        buy1_quantity = int(fields[16])
        # 计算涨停价（昨收的1.1倍，四舍五入保留2位小数）
        zt_price = round(prev_close * 1.1, 2)
        result = {
           "code": code,
            "buy1_price": buy1_price,
            "buy1_quantity": buy1_quantity,
            "zt_price": zt_price
        }
        results.append(result)
    return results


wsUrl = "ws://121.43.57.182:21967/?token=fb6d25972a7bb566a74cf69c853e5d74"
#分配服务器方法请参考：jvQuant.com/wiki/开始使用/分配服务器.html

ws = websocket.WebSocketApp(wsUrl,
                            on_open=on_open,
                            on_data=on_message,
                            on_error=on_error,
                            on_close=on_close)


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
    price = data['buy1_price']
    name = ''
    # enable_balance = 190000
    # enable_balance = get_balance()
    enable_balance = 30000
    rs = buy_info(code, float(price), enable_balance, name, zt_price)
    return rs


# 获取可用资金
def get_balance():
    balance = user.balance[0]
    # 可用资金  预留300
    enable_balance = balance.enable_balance
    return enable_balance


if __name__ == '__main__':
    while True:
        # 获取当前时间
        now = datetime.now().time()
        # 设定一个指定的时间点，比如 14:30
        target_time = datetime.strptime("09:27", "%H:%M").time()
        # 判断当前时间是否大于指定时间
        if now >= target_time:
            break
        time.sleep(5)

    codes = get_codes()
    print(f'=====共有{len(codes)}只股票=====')
    ws.run_forever()
    # while True:
    #     ws.run_forever()
    #     # 获取数据
    #     # data = get_data(codes)
    #     # 如果数据为空，打印信息并继续
    #     if len(data) == 0:
    #         time.sleep(0.5)
    #         print(f'====执行====')
    #         continue
    #     # 执行买入操作
    #     buy(data)
    #     break