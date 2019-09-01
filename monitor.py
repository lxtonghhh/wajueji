"""
后台监控
db
report_info_coll
date->str
time->str
datetime->datetime
info->str

system_var_coll
key->str
value->
"""
from mongo import MongoConn, MONGODB_CONFIG
from datetime import datetime
import time
from sender import send_message

REPORT_TIME = ["0", "8", "16"]
#REPORT_TIME = [str(x) for x in range(60)]


def p(string):
    print(string)


class Monitor(object):
    def __init__(self):
        # hour
        self.time_to_check = None
        self.conn = MongoConn(config=MONGODB_CONFIG)
        self._init_check_time_from_db()

    def _init_check_time_from_db(self):

        conn = MongoConn(config=MONGODB_CONFIG)
        coll = conn.get_coll("system_var_coll")
        doc = coll.find_one(filter=dict(key="report_check_time"))
        if not doc:
            self.time_to_check = REPORT_TIME[0]
            coll.insert(dict(key="report_check_time", value=REPORT_TIME[0]))
        else:
            self.time_to_check = doc['value']

    def restart(self):
        self._init_check_time_from_db()
        self.conn = MongoConn(config=MONGODB_CONFIG)
        self.prepare()

    def prepare(self):
        pass

    def run(self):
        while True:
            try:
                self.report()
                time.sleep(1)
            except:
                self.restart()
                time.sleep(1)

    def run_test(self):
        while True:
            self.report()
            time.sleep(1)

    def get_info(self):
        info = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(info)
        return info

    def report(self):
        def _check_need(time):
            _time = str(int(time.split(":")[0]))
            print(_time, self.time_to_check)
            if _time == self.time_to_check:
                return True
            else:
                return False

        def _update_check_time():
            i = REPORT_TIME.index(self.time_to_check)
            if i >= len(REPORT_TIME) - 1:
                new_time = REPORT_TIME[0]
            else:
                new_time = REPORT_TIME[i + 1]
            self.time_to_check = new_time
            coll = self.conn.get_coll("system_var_coll")
            coll.update({"key": "report_check_time"}, {"$set": {"value": new_time}})
            print("更新", new_time)

        coll = self.conn.get_coll("report_info_coll")
        _date = datetime.now().strftime("%Y-%m-%d")
        _time = datetime.now().strftime("%H:%M:%S")
        if _check_need(_time):
            _update_check_time()
            info = self.get_info()
            coll.insert(dict(date=_date, time=_time, datetime=datetime.now(), info=info))
            send_message(subject="系统状态报告", content=info, attachments=[])
        else:
            print("不需要更新", _time)
            pass


def main():
    m = Monitor()
    m.run()


if __name__ == "__main__":
    main()
