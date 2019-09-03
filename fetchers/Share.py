import requests, json, time, re
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}
SHARES = ["sz000651", "sz002023", "sh600183", "sz300456", "sz002174", "sh600886", "sh601069"]
URL = "https://hq.sinajs.cn/list={0}".format(",".join(SHARES))
TICK = 5
"""
9.3
sz300310
sz300350
sz300148
sh601236
sh600667
sz002726
sz002547
sz300168
sz002261
sz002077
sz000415
sz000558
sh600801
sz300346
sz000859
sz000789
sz000561
sz002465
sh600720
sz300527
sh600797
sz300101
sz002340
sz000672
sz000157
sz000818
sz000836
sz000851
sh601919
sh603636
sh600171
"""

def Share_prepare(self):
    self.conn = MongoConn(config=MONGODB_CONFIG)
    self.c = 0


def Share_work(self):
    print("Make a request Share", URL)
    r = requests.get(url=URL, headers=HEADERS, timeout=5)
    if r.status_code != 200:
        print(1)
        raise Exception
    else:
        self.c = 0
    res = r.text.strip().split("\n")
    for line in res:
        share_name = re.search(pattern="hq_str_\w{2}\d{6}", string=line, flags=0).group().split("_")[2]
        _data = line.split("\"")[1].split(",")

        """
        格力电器,56.950,55.500,57.360,57.820,56.700,57.350,57.360,41492380,2373679523.290,7936,57.350,11200,57.340,
        11300,57.330,6600,57.320,5000,57.310,18000,57.360,50900,57.370,44900,57.380,32000,57.390,128900,57.400,
        2019-09-02,11:30:00,00
        """
        _name, _open, _close, _price, _date = _data[0], float(_data[1]), float(_data[2]), float(_data[7]), _data[-1]

        _change = (_price - _close) / _close
        doc = dict(code=share_name, name=_name, open=_open, close=_close, price=_price, change=_change, date=_data)
        coll = self.conn.get_coll("Share_" + share_name + "_coll")
        coll.insert(doc)
        print(doc)
    time.sleep(TICK)


def Share_exception(self):
    self.c += 1
    if self.c > 3:
        print("Fail request too many times")
        time.sleep(5 * TICK)
    else:
        print("Fail request")
        pass


def test_meta():
    newFetcher = create_new_fetcher("ShareFetcher", Share_prepare, Share_work, Share_exception)
    n = newFetcher()
    print(n.name, n.uuid)
    n.run()
    exit(1)


if __name__ == "__main__":
    test_meta()
    # fetcher_main()
