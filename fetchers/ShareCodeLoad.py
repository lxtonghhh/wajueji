import requests, json, time, re
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher
from bs4 import BeautifulSoup
from fetchers.pool import SHARE_LIST_ALL, SHARE_LIST_PART

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}
proxies = {"http": "http://127.0.0.1:9090", "https": "http://127.0.0.1:9090", }
URL = "https://cn.investing.com/stock-screener/?sp=country::37|sector::a|industry::a|equityType::a|exchange::a|last::0,21%3Ceq_market_cap;2"
PLACE = {"上海": "sh", "深圳": "sz"}
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
    # https://cn.investing.com/stock-screener/?sp=country::37|sector::a|industry::a|equityType::a|exchange::a|last::0,21%3Ceq_market_cap;2
    with open(fname, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        list = soup.select("#resultsTable")[0].tbody.find_all("tr")
        # print(list)
        print([i.a['href'].split("/")[-1] for i in list])
        # print([i for i in list])


def f():
    SHARE_INFO_LIST = []
    for share in SHARE_LIST_ALL:

        while True:
            try:
                r = requests.get(url="https://cn.investing.com/equities/" + share + "-technical", headers=HEADERS,
                                 timeout=5)
                if r.status_code != 200:
                    print("Fail request")
                    time.sleep(3)
                    continue
                else:
                    pass
                soup = BeautifulSoup(r.text, 'html.parser')
                _pair_id = soup.find_all("div", class_="headBtnWrapper float_lang_base_2 js-add-alert-widget")[0][
                    'data-pair-id']
                _place = soup.find_all("i", class_="btnTextDropDwn arial_12 bold")[0].string
                _title = re.search(r"\d{6}",
                                   soup.find_all("h1", class_="float_lang_base_1 relativeAttr")[0].string, ).group()
                _name = soup.find_all("i", class_="btnTextDropDwn arial_12 bold")[0].string + "_" + \
                        soup.find_all("h1", class_="float_lang_base_1 relativeAttr")[0].string
                _code = PLACE[_place] + _title
                print({"url_name": share, "pair_id": _pair_id, "name": _name, "code": _code})
                SHARE_INFO_LIST.append({"url_name": share, "pair_id": _pair_id, "name": _name, "code": _code})
                time.sleep(1 )
                break
            except:
                time.sleep(3)
                print("Fail request")
                continue
    print(SHARE_INFO_LIST)
    with open("share.json", "w", encoding="utf-8") as f:
        json.dump(SHARE_INFO_LIST, f)


if __name__ == "__main__":
    # load_href_from_local_html("1.html")
    r = requests.get(url="https://cn.investing.com/equities/" + "china-life-ss" + "-technical", headers=HEADERS,
                     timeout=5)
    f()
