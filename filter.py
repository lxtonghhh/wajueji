import uuid, datetime
from mongo import MongoConn, MONGODB_CONFIG
import inspect


class Filter(object):
    def __init__(self):
        self.pool = []

    def add(self, obj):
        """

        :param obj: {code,name}
        :return:
        """
        self.pool.append(obj)

    def work(self):
        pass

    def result(self):
        print("###策略{0}筛选结果###".format(self.name))
        for i in self.pool:
            print("-->", i)
        return self.pool

    def codes(self):
        return [i["code"] for i in self.pool]


def create_new_filter(strategy_name, strategy_method):
    new_filter = type(strategy_name + "Filter", (Filter,),
                      dict(work=strategy_method, name=strategy_name))
    return new_filter


def s(self, a, b):
    if a > 1:
        self.pool.append(1)


if __name__ == "__main__":
    f = create_new_filter(s)()
    f.work(a=2, b=2)
    f.result()
