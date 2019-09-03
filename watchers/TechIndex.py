import requests, json, time, re, math
from datetime import datetime
from mongo import MongoConn, MONGODB_CONFIG
from sender import send_message
from fetcher import create_new_fetcher
"""
('上海_润达医疗 (603108)\t', 'sh603108', 23)
('上海_中国高科 (600730)\t', 'sh600730', 22)
('深圳_山东龙大肉食品股份有限公司 (002726)\t', 'sz002726', 22)
('深圳_大唐高鸿数据网络技术股份有限公司 (000851)\t', 'sz000851', 23)
('深圳_莱茵达体育发展股份有限公司 (000558)\t', 'sz000558', 22)
('深圳_江西万年青水泥股份有限公司 (000789)\t', 'sz000789', 22)
('深圳_浙江星星科技股份有限公司 (300256)\t', 'sz300256', 23)
('深圳_苏州锦富技术股份有限公司 (300128)\t', 'sz300128', 22)
('上海_东方通信 (600776)\t', 'sh600776', 22)
('上海_梅雁吉祥 (600868)\t', 'sh600868', 23)
('深圳_甘肃上峰水泥股份有限公司 (000672)\t', 'sz000672', 22)
('上海_祁连山 (600720)\t', 'sh600720', 22)
('深圳_光正集团股份有限公司 (002524)\t', 'sz002524', 22)
('深圳_成都振芯科技股份有限公司 (300101)\t', 'sz300101', 22)
('上海_皖江物流 (600575)\t', 'sh600575', 22)
('深圳_河南华英农业发展股份有限公司 (002321)\t', 'sz002321', 23)
('深圳_安徽国风塑业股份有限公司 (000859)\t', 'sz000859', 23)
('上海_南威软件 (603636)\t', 'sh603636', 23)
('上海_金隅集团 (601992)\t', 'sh601992', 22)
('上海_华新水泥 (600801)\t', 'sh600801', 23)
('深圳_万达信息股份有限公司 (300168)\t', 'sz300168', 23)
('深圳_江苏金通灵流体机械科技股份有限公司 (300091)\t', 'sz300091', 23)
('深圳_蓝思科技股份有限公司 (300433)\t', 'sz300433', 23)
('深圳_北京数码视讯科技股份有限公司 (300079)\t', 'sz300079', 22)
('深圳_航锦科技股份有限公司 (000818)\t', 'sz000818', 23)
('深圳_武汉力源信息技术股份有限公司 (300184)\t', 'sz300184', 22)
('上海_广深铁路 (601333)\t', 'sh601333', 23)
('上海_金健米业 (600127)\t', 'sh600127', 22)
('深圳_北京四维图新科技股份有限公司 (002405)\t', 'sz002405', 23)
('深圳_深圳中华自行车（集团）股份有限公司 (000017)\t', 'sz000017', 22)
('上海_长电科技 (600584)\t', 'sh600584', 22)
('深圳_江苏润和软件股份有限公司 (300339)\t', 'sz300339', 22)
('深圳_中国船舶重工集团应急预警与救援装备股份有限公司 (300527)\t', 'sz300527', 22)
"""
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}
SHARES = ["sz002156", "sh600063", "sh600704", "sh603108", "sh600797", "sz002649", "sh600730", "sz002519"]
URL = "https://hq.sinajs.cn/list={0}".format(",".join(SHARES))
TICK = 5

STATUS = {s: 0 for s in SHARES}


def Share_prepare(self):
    self.conn = MongoConn(config=MONGODB_CONFIG)
    self.c = 0


def Share_work(self):
    # print("Make a request Share", URL)
    r = requests.get(url=URL, headers=HEADERS, timeout=5)
    if r.status_code != 200:
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
        _change = (_price - _open) / _open
        # 涨跌幅监控 关键点为-3 -2 -1 0 1 2 3
        _status = STATUS[share_name]
        if _change < 0:
            # -1.2->-1.0
            ns = math.ceil(_change * 100)
        elif _change > 0:
            # 1.2->1.0
            ns = math.floor(_change * 100)
        else:
            ns = 0
        #print(_name, "涨跌幅为:", round(_change, 4) * 100, "% 当前状态:", ns)
        if ns == _status:
            # 状态不变
            pass
        else:
            STATUS[share_name] = ns
            print("->", _name, "涨跌幅为:", round(_change, 4) * 100, "% 更新状态:", ns)
            doc = dict(code=share_name, name=_name, change=_change, date=_data)
            coll = self.conn.get_coll("Share_" + share_name + "_change_coll")
            coll.insert(doc)
            send_message(subject="价格监控-" + _name, content=round(_change, 4), attachments=[])
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


if __name__ == "__main__":
    test_meta()
    # fetcher_main()
