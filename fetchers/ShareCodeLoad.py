import requests, json, time, re
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}

URL = "https://cn.investing.com/stock-screener/?sp=country::37|sector::a|industry::a|equityType::a|exchange::a|last::0,21%3Ceq_market_cap;2"

TICK = 5


def Share_prepare(self):
    self.conn = MongoConn(config=MONGODB_CONFIG)
    self.c = 0


def Share_work(self):
    print("Make a request Share", URL)
    r = requests.get(url=URL, headers=HEADERS, timeout=5)

    if r.status_code != 200:
        raise Exception
    else:
        self.c = 0
    with open("2.html", "r") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        tech_list = soup.select("#resultsTable")
        print(tech_list)
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
    n.run_test()
    exit(1)
def load_href_from_local_html(fname):
    #https://cn.investing.com/stock-screener/?sp=country::37|sector::a|industry::a|equityType::a|exchange::a|last::0,21%3Ceq_market_cap;2
    with open(fname, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        list = soup.select("#resultsTable")[0].tbody.find_all("tr")
        #print(list)
        print([i.a['href'].split("/")[-1] for i in list])
        #print([i for i in list])

if __name__ == "__main__":

    load_href_from_local_html("11.html")

