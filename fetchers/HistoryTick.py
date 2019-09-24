# 获取tick历史数据
# 来自新浪财经
import requests, json, time, re, demjson, math, random
from mongo import MongoConn, MONGODB_CONFIG
from fetcher import create_new_fetcher, ExitSignal, HEADERS

MA_DICT = {5: "5", 10: "10", 15: "15", 20: "20", 25: "25", }
INTERVAL_DICT = {5: "5", 15: "15", 30: "30", 60: "60", }  # 间隔分钟
# 每天交易4小时 一天有48个5分钟数据 16个15分钟数据 8个30分钟数据 4个60分钟数据 datalen最大限制为200
PARAMS_50_day_by_60m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[60], datalen=4 * 50)
PARAMS_10_day_by_15m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[15], datalen=16 * 10)
PARAMS_4_day_by_5m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[5], datalen=48 * 4)
PARAMS_3_day_by_5m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[5], datalen=48 * 3)
PARAMS_2_day_by_5m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[5], datalen=48 * 2)
PARAMS_1_day_by_5m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[5], datalen=48 * 1)

HISTORY_URL = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?" \
              "symbol={share}&scale={interval}&ma={MA}&datalen={datalen}"
PARAMS_IN_USE = PARAMS_1_day_by_5m

SHARES_IN_USE = []

PORTFOLIO_LIST_FILE = "portfolio_list.json"


def make_portfolio_list(fname=PORTFOLIO_LIST_FILE, share_list=SHARES_IN_USE, is_all=True):
    """
    生成组合名单
    :param fname:
    :param share_list: 目标share名单
    :param is_all: 获取全部
    :return:
    """
    # 本地share代码表
    with open("../local/share.json", "r", encoding="utf-8", ) as f:
        all_share_dict = json.load(f)
    output = []
    if is_all:
        for ss in all_share_dict:
            output.append(dict(name=ss["name"], code=ss["code"]))
    else:
        for s in share_list:
            for ss in all_share_dict:
                if s == ss["code"]:
                    output.append(dict(name=ss["name"], code=ss["code"]))
                    break
                else:
                    continue
    with open(fname, "w", encoding="utf-8", ) as f:
        json.dump(output, f)
    return output


def Share_prepare(self):
    def load_share_list_from_json(fname):
        with open(fname, "r", encoding="utf-8") as f:
            l = json.load(f)
            return [(i["name"], i["code"]) for i in l]

    self.conn = MongoConn(config=MONGODB_CONFIG)
    self.c = 0

    self.share_list = load_share_list_from_json(PORTFOLIO_LIST_FILE)

    self.cur_share_idx = 0
    self.cur_share = self.share_list[self.cur_share_idx]

    self.datas = []


def Share_work(self):
    _name = self.cur_share[0]
    _code = self.cur_share[1]
    _interval, _MA, _datalen = PARAMS_IN_USE["interval"], PARAMS_IN_USE["MA"], PARAMS_IN_USE["datalen"]
    print(HISTORY_URL.format(share=_code, interval=_interval, MA=_MA, datalen=_datalen))
    r = requests.get(url=HISTORY_URL.format(share=_code, interval=_interval, MA=_MA, datalen=_datalen),
                     headers=HEADERS, timeout=5)
    if r.status_code != 200:
        print(r.status_code)
        raise Exception
    else:
        self.c = 0
    res = demjson.decode(r.text, encoding="utf-8")

    opens = [float(line["open"]) for line in res]
    highs = [float(line["high"]) for line in res]
    lows = [float(line["low"]) for line in res]
    closes = [float(line["close"]) for line in res]
    name = [_name for line in res]
    self.datas.append(list(zip(opens, highs, lows, closes, name)))


def Share_on_tick(self):
    if self.cur_share_idx == len(self.share_list) - 1:
        self.result = self.datas
        raise ExitSignal

    self.cur_share_idx = self.cur_share_idx + 1 if self.cur_share_idx < len(self.share_list) - 1 else 0
    self.cur_share = self.share_list[self.cur_share_idx]
    time.sleep(2 * random.random())


def Share_exception(self):
    self.c += 1
    if self.c > 3:
        print("Fail request too many times")
        time.sleep(5)
    else:
        print("Fail request")
        pass


def scan_tick_data(is_test=False, is_all=False):
    name_code_map = make_portfolio_list(is_all=is_all)
    newFetcher = create_new_fetcher("TickDataFetcher", Share_prepare, Share_work, Share_exception, Share_on_tick)
    n = newFetcher()
    print(n.name, n.uuid)
    if is_test:
        res = n.run_test()
    else:
        res = n.run()

    """
    data -> dict
        info:dict {
        size:int数据的tick大小(5 15 30 60)间隔分钟,
        start:date开始时间,
        end:date结束时间,
        map:list标的名称和代码映射
            [{"name":...,"code":...},{"name":...,"code":...}],
        content:list [
            [(share1_open_tick1, high1, low1, close1),(share1_open_tick2, high2, low2, close2),...],
            [(share2_open_tick1, high1, low1, close1),(share2_open_tick2, high2, low2, close2),...],
            [(share3_open_tick1, high1, low1, close1),(share3_open_tick2, high2, low2, close2),...],
            ]
    """
    with open("../app/output.json", "w", encoding="utf-8") as f:
        data = dict()
        data["info"] = dict(size=PARAMS_IN_USE["MA"], start=None, end=None, map=name_code_map)
        data["content"] = res
        json.dump(data, f)

    return res


if __name__ == "__main__":
    print(random.random())

    scan_tick_data(is_test=False, is_all=True)
