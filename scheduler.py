from mongo import MongoConn, MONGODB_CONFIG
from datetime import datetime
import time, sys
from sender import send_message
from utils.date import time_to_str
from utils.common import get_args, get_exception_info, tuples_to_str_list
from fetchers.TechIndex import scan_share
from utils.process import daemonize

REPORT_TIME = [str(i) for i in range(24)]


# REPORT_TIME = [str(x) for x in range(60)]


def p(string):
    print(string)
    return string


class Scheduler(object):
    def __init__(self, func=None, *args, **kwargs):
        # hour
        self.time_to_check = None
        self.conn = MongoConn(config=MONGODB_CONFIG)
        self._init_check_time_from_db()

        self.func = func

    def _init_check_time_from_db(self):

        conn = MongoConn(config=MONGODB_CONFIG)
        coll = conn.get_coll("system_var_coll")
        doc = coll.find_one(filter=dict(key="report_check_time"))
        if not doc:
            # 寻找最近将来时间点 默认有序
            _now_hour = datetime.now().hour
            for h in REPORT_TIME:
                if _now_hour - int(h) > 0:
                    continue
                else:
                    self.time_to_check = h
                    break
            if not self.time_to_check:
                self.time_to_check = REPORT_TIME[0]
            coll.insert(dict(key="report_check_time", value=self.time_to_check))
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
            except Exception as e:
                send_message(subject="系统错误报告", content=[get_exception_info(e)], attachments=[])
                self.restart()

    def run_test(self):
        while True:
            self.report(is_test=True)
            time.sleep(1)

    def get_info(self, is_test):
        res = scan_share(is_test)

        info_str = time_to_str(datetime.now()) + "\n" + "\n".join(tuples_to_str_list(res))
        return info_str

    def report(self, is_test=False):
        def _check_need(time):
            _time = str(int(time.split(":")[0]))
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

            conn = MongoConn(config=MONGODB_CONFIG)
            coll = conn.get_coll("system_var_coll")
            coll.update({"key": "report_check_time"}, {"$set": {"value": new_time}})

        _date = datetime.now().strftime("%Y-%m-%d")
        _time = datetime.now().strftime("%H:%M:%S")
        if _check_need(_time):
            _update_check_time()

            # 执行
            info = self.get_info(is_test)

            send_message(subject="定时任务执行报告", content=info, attachments=[])
            conn = MongoConn(config=MONGODB_CONFIG)
            coll = conn.get_coll("report_info_coll")
            coll.insert(dict(date=_date, time=_time, datetime=datetime.now(), info=info))

        else:
            pass


def main():
    m = Scheduler()
    m.run()


def main_test():
    m = Scheduler()
    m.run_test()


if __name__ == "__main__":
    daemonize(func=main)
