import requests, json, time
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}
ts2local = lambda ts: datetime.fromtimestamp(ts / 1000)
GOLD_URL = "https://data-asg.goldprice.org/dbXRates/USD"
TICK = 1


def XAUPrice_prepare(self):
    self.conn = MongoConn(config=MONGODB_CONFIG)
    self.xauPrice_coll = self.conn.get_coll("xauPrice_coll")
    self.base_coll = self.conn.get_coll("base_coll")
    base_doc = self.base_coll.find_one(dict(name="xauPrice"))
    self.base = base_doc['value'] if base_doc else 0
    print("xauPrice base:", self.base)
    self.c = 0


def XAUPrice_work(self):
    print("Make a request XAUPrice_work")
    r = requests.get(url=GOLD_URL, headers=HEADERS, timeout=5)
    if r.status_code != 200:
        raise Exception
    else:
        self.c = 0
    d = r.json()
    ts, xauPrice = d['ts'], d['items'][0]['xauPrice']
    print(ts2local(ts), d['items'][0]['xauPrice'], d['items'][0]['xauClose'])
    self.xauPrice_coll.insert(
        dict(time=ts2local(ts), xauPrice=d['items'][0]['xauPrice'], xauClose=d['items'][0]['xauClose']))
    if not self.base:
        self.base_coll.insert(dict(name="xauPrice", value=xauPrice))
        self.base = xauPrice
    delta = xauPrice - self.base

    if self.base and abs(delta) / self.base > 0.01:
        print("触发了涨跌事件:黄金价格-" + "下跌" if delta < 0 else "上涨" + ",幅度: " + str(abs(delta) * 100 / self.base) + "%")
        self.base = xauPrice
        self.base_coll.update(dict(name="xauPrice"), {'$set': dict(value=xauPrice)}, upsert=True)
        send_message(subject="黄金价格-" + "下跌" if delta < 0 else "上涨", content=str(abs(delta) * 100 / self.base) + "%",
                     attachments=[])
    time.sleep(TICK)


def XAUPrice_exception(self):
    self.c += 1
    if self.c > 3:
        print("Fail request too many times")
        time.sleep(5 * TICK)
    else:
        print("Fail request")
        pass


def test_meta():
    newFetcher = create_new_fetcher("XAUPriceFetcher", XAUPrice_prepare, XAUPrice_work, XAUPrice_exception)
    n = newFetcher()
    print(n.name, n.uuid)
    n.run()
    exit(1)


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
    test_meta()
    # fetcher_main()
