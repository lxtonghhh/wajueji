import requests, json, time
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}
ts2local = lambda ts: datetime.fromtimestamp(ts / 1000)
GOLD_URL = "https://data-asg.goldprice.org/dbXRates/USD"
TICK = 1
import sys


def get_cur_info():
    print(sys._getframe().f_code.co_filename)  # 当前文件名
    print(sys._getframe(0).f_code.co_name)  # 当前函数名
    print(sys._getframe(1).f_code.co_name)  # 调用该函数的函数的名字，如果没有被调用，则返回module
    print(sys._getframe().f_lineno)  # 当前行号


def fetcher_main():

    conn = MongoConn(config=MONGODB_CONFIG)
    xauPrice_coll = conn.get_coll("xauPrice_coll")
    base_coll = conn.get_coll("base_coll")
    base_doc = base_coll.find_one(dict(name="xauPrice"))
    base = base_doc['value'] if base_doc else 0
    print("xauPrice base:", base)
    c = 0
    while True:
        try:
           
            print("Make a request")
            r = requests.get(url=GOLD_URL, headers=HEADERS, timeout=5)
            if r.status_code != 200:
                raise Exception
            else:
                c = 0
            d = r.json()
            ts, xauPrice = d['ts'], d['items'][0]['xauPrice']
            print(ts2local(ts), d['items'][0]['xauPrice'], d['items'][0]['xauClose'])
            xauPrice_coll.insert(
                dict(time=ts2local(ts), xauPrice=d['items'][0]['xauPrice'], xauClose=d['items'][0]['xauClose']))
            if not base:
                base_coll.insert(dict(name="xauPrice", value=xauPrice))
                base = xauPrice
            delta = xauPrice - base
            if base and abs(delta) / base > 0.01:
                print("触发了涨跌事件:黄金价格-" + "下跌" if delta < 0 else "上涨" + ",幅度: " + str(abs(delta) * 100 / base) + "%")
                base = xauPrice
                base_coll.update(dict(name="xauPrice"), {'$set': dict(value=xauPrice)}, upsert=True)
                send_message(subject="黄金价格-" + "下跌" if delta < 0 else "上涨", content=str(abs(delta) * 100 / base) + "%",
                             attachments=[])
            time.sleep(TICK)
        except:
            c += 1
            if c > 3:
                print("Fail request too many times")
                time.sleep(5 * TICK)
            else:
                print("Fail request")
                pass


if __name__ == "__main__":
    fetcher_main()
