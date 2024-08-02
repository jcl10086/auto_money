import requests
import json


def wx_push(content):
    url = "https://wxpusher.zjiecode.com/api/send/message"

    payload = json.dumps({
        "appToken": "AT_GfooTh9LONk6o4TKbeVtClOlQfQuz5N4",
        "content": content,
        "summary": content,
        "contentType": 1,
        "uids": [
            "UID_ld2fuw8pCxJlLyugTNn7BLzgSW8q"
        ],
        "verifyPay": False
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)


if __name__ == '__main__':
    wx_push('test')