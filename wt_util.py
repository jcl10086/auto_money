import requests


def get_wsurl(code):
    url = "http://jvQuant.com/query/server?market=ab&type=sql&token=72ecd45a88652271818f3e8411c11e0a"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    url = response.json()['server'] + '/sql?mode=order_book&code=' + code + '&token=72ecd45a88652271818f3e8411c11e0a'
    return url


def get_wt_num(url):
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    return data


def resolve_data(data, zt_price):
    # 筛选条件：类型为"B"且交易量>5000
    filtered_list = [
        record for record in data["data"]["list"]
        if record[3] == "B" and record[2] > 100000  and record[1] == zt_price
    ]
    return filtered_list


def wt_core(code, zt_price):
    url = get_wsurl(code)
    data = get_wt_num(url)
    filtered_list = resolve_data(data, zt_price)
    return filtered_list


if __name__ == '__main__':
    wt_core('002329', 4.53)