# 获取tick历史数据
# 来自新浪财经
import requests, json, time, re, demjson, math
from datetime import datetime
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

# 计算一段时间内组合的最大回撤和最终收益
LQC_LIST = ["sz000725", "sh600775", "sz002456"]  # 9.9

TECH_LIST98 = ["sh600590", "sz000909", "sh601138", "sh600501", "sz300424", "sh600088", "sh600428",
               "sz300589", "sz300551", "sh600967", "sh603636", "sz300095", "sh600719", "sh601949", "sz300034",
               "sz000561", "sz300253", "sh600642", "sz002023", "sz002246", "sz300026", "sz002177", "sh603108",
               "sz002361", "sz000877"]  # 9.8
TECH_LIST99 = ['sz000877', 'sh600766', 'sh601989', 'sz300328', 'sz300316', 'sh600597', 'sz300103', 'sz000032',
               'sz000012', 'sz300095', 'sz300551', "sz000725"]  # 9.9
TECH_LIST99_QUICK = ['sz300202', 'sz002177', 'sh600422', 'sz300561', 'sz000566', 'sh600660', 'sh603399', 'sz002048',
                     'sz300235', 'sz002657', 'sh600146']  # 9.9收盘前1小时
TECH_LIST910_QUICK2 = ['sz002455', 'sz000830', 'sz300278', 'sh603993', 'sh600178', 'sz000639', 'sh600549', 'sh600277',
                       'sh603299', 'sz002310',
                       'sz300390', 'sz002645', 'sh600800', 'sz002104', 'sh600108', 'sz000595', 'sz300016', 'sz000032',
                       'sz002556', 'sz002342',
                       'sh600111', 'sh600467', 'sz002167', 'sz300455', 'sz300386', 'sz300264', 'sz002755']  # 9.9收盘前2小时
TECH_LIST910_QUICK = ['sz002233', 'sz000930', 'sz002010', 'sz002019', 'sz300376', 'sz002310', 'sz300390', 'sz002100',
                      'sh600589', 'sh600339',
                      'sz000955', 'sz002625', 'sh600963', 'sz002582', 'sh600307', 'sz002556', 'sz002385', 'sz300152',
                      'sz002075', 'sz002218',
                      'sz002182', 'sz002340']  # 9.9收盘前1小时
TECH_LIST916_QUICK2 = ['sz300079', 'sz300198', 'sh600277', 'sh601567', 'sz002174', 'sz000607', 'sh600502', 'sh600722',
                       'sh600635', 'sz300101',
                       'sz002318', 'sz300063', 'sh600797', 'sh600409', 'sh601928', 'sz002079', 'sz000606', 'sh600730',
                       'sh600350', 'sz300339',
                       'sz002137', 'sz002296', 'sh600376', 'sz300118']  # 9.16收盘前2小时

TECH_LIST920_QUICK2 = ['sh600197', 'sh601800', 'sz300042', 'sh601231', 'sh600237', 'sz300365', 'sh600557', 'sh600720',
                       'sh600516']  # 9.20收盘前2小时
TECH_LIST920_QUICK1 = ['sz002589', 'sh600355', 'sh600237', 'sh600720']  # 9.20收盘前1小时
TECH_LIST920 = ['sz002273', 'sz000601', 'sz002378']  # 9.20收盘前1日
SHARES_IN_USE = TECH_LIST920

PORTFOLIO_LIST_FILE = "portfolio_list.json"


def make_json(fname=PORTFOLIO_LIST_FILE, share_list=SHARES_IN_USE):
    with open("fetchers/share.json", "r", encoding="utf-8", ) as f:
        share_dict = json.load(f)
    output = []
    for s in share_list:
        for ss in share_dict:
            if s == ss["code"]:
                output.append(dict(name=ss["name"], code=ss["code"]))
                break
            else:
                continue
    print(output)
    with open(fname, "w", encoding="utf-8", ) as f:
        json.dump(output, f)
    return output


def make_portfilio():
    pass


def load_share_list_from_json(fname):
    with open(fname, "r", encoding="utf-8") as f:
        l = json.load(f)
        return [(i["name"], i["code"]) for i in l]


def Share_prepare(self):
    self.conn = MongoConn(config=MONGODB_CONFIG)
    self.c = 0

    # [(i["name"], i["code"])]
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


def Share_exception(self):
    self.c += 1
    if self.c > 3:
        print("Fail request too many times")
        time.sleep(5)
    else:
        print("Fail request")
        pass


def scan_tick_data(is_test=False):
    newFetcher = create_new_fetcher("TickDataFetcher", Share_prepare, Share_work, Share_exception, Share_on_tick)
    n = newFetcher()
    print(n.name, n.uuid)
    if is_test:
        return n.run_test()
    else:
        return n.run()


def jsonfy(s: str) -> object:
    # {day:"2019-07-03 10:30:00",open:"12.450",high:"12.450",low:"12.200",close:"12.290",volume:"8370626"}
    # 此函数将不带双引号的json的key标准化
    """
    使用以下库解析key不带双引号的json
    obj=demjson.decode(text encoding="utf-8")
    :param s:
    :return:
    """
    obj = eval(s, type('js', (dict,), dict(__getitem__=lambda s, n: n))())
    return obj


if __name__ == "__main__":
    name_code_map = make_json()
    res = scan_tick_data(is_test=True)
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
    with open("./app/output.json", "w", encoding="utf-8") as f:
        data = dict()
        data["info"] = dict(size=PARAMS_IN_USE["MA"], start=None, end=None, map=name_code_map)
        data["content"] = res
        json.dump(data, f)
