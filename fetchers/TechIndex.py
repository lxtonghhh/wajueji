import requests, json, time, re
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher, ExitSignal
from filter import create_new_filter
from bs4 import BeautifulSoup
from utils.date import GMT_to_local, get_month, get_day, get_hour, get_minute, get_second, get_year, time_to_str
from fetchers.pool import SHARE_LIST_ALL, SHARE_LIST_PART
from constant import ROOT_DIR

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}
HEADERS_FOR_FORM = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest'
}
POST_URL = "https://cn.investing.com/instruments/Service/GetTechincalData"
PERIOD = "86400"  # 86400一日 3600一小时
HEADERS_IN_USE = HEADERS_FOR_FORM
URL_IN_USE = POST_URL

SHARE_URL_LIST_IN_USE = SHARE_LIST_ALL
URL = "https://cn.investing.com/equities/"
TICK = 2
PLACE = {"上海": "sh", "深圳": "sz"}


def load_share_info_from_json():
    with open(ROOT_DIR + "local/share.json", "r", encoding="utf-8") as f:
        obj = json.load(f)
        return {i["url_name"]: (i["pair_id"], i["name"], i["code"]) for i in obj}


def strategy_multi_MA(self, code, name, MA5, MA10, MA20, MA50):
    """
    使用移动MA5,10,20,50依次按顺序排列，表示多头并进，视为买入信号
    :return:
    """

    if MA5 > MA10 and MA10 > MA20 and MA20 > MA50:
        print("-->检查策略MA", code, name, MA5, MA10, MA20, MA50, "符合")
        self.add({"code": code, "name": name})
    else:
        pass


def Share_prepare(self):
    self.conn = MongoConn(config=MONGODB_CONFIG)
    self.coll = self.conn.get_coll("share_tech_coll")
    self.cur_share_idx = 0
    self.cur_share = SHARE_URL_LIST_IN_USE[self.cur_share_idx]
    self.c = 0
    # {'anhui-ankai-a': ('944008', '深圳_安徽安凯汽车股份有限公司 (000868)\t', 'sz000868')}
    self.share_dict = load_share_info_from_json()

    self.pool = []
    self.result = []

    self.f = create_new_filter("MA", strategy_multi_MA)()

    # 所有采集结果
    self.store = []


def Share_work(self):
    _pair_id = self.share_dict[self.cur_share][0]
    _name = self.share_dict[self.cur_share][1]
    _code = self.share_dict[self.cur_share][2]
    print(_name, _code, _pair_id)

    form_data = dict(pairID=_pair_id, period=PERIOD, viewType="normal")  # day period="86400" hour period="3600"
    # r = requests.get(url=URL + self.cur_share + "-technical", headers=HEADERS, timeout=5)
    r = requests.post(url=URL_IN_USE, data=form_data, headers=HEADERS_IN_USE, timeout=5)
    if r.status_code != 200:
        print("Request Fail: ", r.status_code)
        raise Exception
    else:
        self.c = 0
    soup = BeautifulSoup(r.text, 'html.parser')

    tech_list = soup.select("#curr_table")[1].tbody.find_all("tr", )[0:-1]
    _info = {}
    buy_c, sell_c, excessive_sell_num, excessive_buy_num = 0, 0, 0, 0
    for i in tech_list:
        __index = i.find_all('td')[0].string
        __value = i.find_all('td')[1].string
        __signal = i.span.string.strip()
        _info[__index] = {"value": __value, "signal": __signal}
        if __signal == "购买":
            buy_c += 1
        elif __signal == "出售":
            sell_c += 1
        elif __signal == "超卖":
            if __value == "CCI(14)":
                excessive_sell_num *= 10
            else:
                excessive_sell_num += 1
        elif __signal == "超买":
            if __value == "CCI(14)":
                excessive_buy_num *= 10
            else:
                excessive_buy_num += 1

    MA_list = soup.select("#curr_table")[2].tbody.find_all("tr", )[0:-1]
    for i in MA_list:
        __index = i.find_all('td')[0].string
        __1 = i.find_all('td')[1]
        __2 = i.find_all('td')[2]
        __signal_std = __1.span.string.strip()
        __signal_move = __2.span.string.strip()
        _info[__index + "标准"] = {"value": __1.text.strip().split("\n")[0], "signal": __signal_std}
        _info[__index + "移动"] = {"value": __2.text.strip().split("\n")[0], "signal": __signal_move}

        if __signal_std == "购买":
            buy_c += 0.25
        elif __signal_std == "出售":
            sell_c += 0.25

        if __signal_move == "购买":
            buy_c += 0.25
        elif __signal_move == "出售":
            sell_c += 0.25

    _info["summary"] = {"buy": buy_c, "sell": sell_c}
    _date = soup.find_all("span", class_="h3TitleDate")[0].string

    self.store.append((_code, time_to_str(GMT_to_local(_date)), buy_c))
    """
    _place = soup.find_all("i", class_="btnTextDropDwn arial_12 bold")[0].string
    _title = re.search(r"\d{6}", soup.find_all("h1", class_="float_lang_base_1 relativeAttr")[0].string, ).group()
    _name = soup.find_all("i", class_="btnTextDropDwn arial_12 bold")[0].string + "_" + \
            soup.find_all("h1", class_="float_lang_base_1 relativeAttr")[0].string
    _code = PLACE[_place] + _title
    """

    # if buy_c > 21:
    if buy_c >= 13.75:
        print("-->", GMT_to_local(_date), _name, _code, " 推荐购买: ", buy_c, " 超卖: ", excessive_sell_num, " 超买: ",
              excessive_buy_num)
        self.pool.append((GMT_to_local(_date), _name, _code, buy_c, excessive_sell_num, excessive_buy_num))
        self.result.append((_code, buy_c))
        if len(self.pool) > 5:
            send_message(subject="推荐-" + "购买指标多", content=self.pool, attachments=[])
            self.pool = []
    # self.coll.update({"name": _name}, {'$set': {"date": _date, "info": _info}}, upsert=True)
    """
    # strategy_multi_MA
    MA_value_list = [float(i.find_all('td')[2].text.strip().split("\n")[0]) for i in MA_list]
    MA5, MA10, MA20, MA50 = MA_value_list[0:4]
    self.f.work(name=_name, code=_code, MA5=MA5, MA10=MA10, MA20=MA20, MA50=MA50)
    """

    if self.cur_share_idx == len(SHARE_URL_LIST_IN_USE) - 1:
        """
        self.f.result()
        # 求交集
        # MA_result = self.f.codes()
        MA_result = self.pool
        Index_result = self.pool
        result = list(set(MA_result) & set(Index_result))
        self.result = result
        
        """
        if len(self.pool) > 0:
            send_message(subject="推荐-" + "超卖", content=self.pool, attachments=[])
        """
        print("######Result:")
        for s in result:
            print(s)
        """
        # 持久化采集结果
        _month, _day, _hour = str(get_month()), str(get_day()), str(get_hour())
        with open(ROOT_DIR + "output/" + _month + "_" + _day + "_" + _hour + "_" + PERIOD + ".json", "w",
                  encoding="utf-8") as f:
            json.dump(self.store, f)

        raise ExitSignal

    self.cur_share_idx = self.cur_share_idx + 1 if self.cur_share_idx < len(SHARE_URL_LIST_IN_USE) - 1 else 0
    self.cur_share = SHARE_URL_LIST_IN_USE[self.cur_share_idx]
    time.sleep(TICK)


def Share_exception(self):
    self.c += 1
    if self.c > 3:
        print("Fail request too many times")
        time.sleep(5 * TICK)
    else:
        print("Fail request")
        time.sleep(TICK)


def test_meta():
    newFetcher = create_new_fetcher("ShareFetcher", Share_prepare, Share_work, Share_exception)
    n = newFetcher()
    print(n.name, n.uuid)
    n.run()
    exit(1)


def scan_share(is_test):
    newFetcher = create_new_fetcher("ShareFetcher", Share_prepare, Share_work, Share_exception)
    n = newFetcher()
    print(n.name, n.uuid, "Start to fetch")
    if is_test:
        res = n.run_test()
    else:
        res = n.run()
    print(n.name, n.uuid, "Finish fetching:", res)
    return res


if __name__ == "__main__":
    # test_meta()
    print("-->扫描结果： ", scan_share(is_test=False))
