import requests, json, time
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher, ExitSignal
import os

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}
URL = "https://cn.investing.com/instruments/Service/GetTechincalData"
BODY = dict(pairID="1152301", period="86400", viewType="normal")
TICK = 1


def Test_prepare(self):
    pass


def Test_work(self):
    r = requests.post(url=URL, data=BODY, headers=HEADERS, timeout=5, verify=False)

    if r.status_code != 200:
        raise Exception
    else:
        self.c = 0
    with open("1.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    raise ExitSignal


def Test_exception(self):
    pass


def test_meta():
    newFetcher = create_new_fetcher("TestFetcher", Test_prepare, Test_work, Test_exception)
    n = newFetcher()
    print(n.name, n.uuid)
    n.run_test()
    exit(1)


if __name__ == "__main__":
    test_meta()
