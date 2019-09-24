import uuid, datetime
from mongo import MongoConn, MONGODB_CONFIG

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    'Accept': '*/*',
}

class ExitSignal(Exception):
    def __init__(self):
        pass


class Fetcher(object):
    def __init__(self):
        self.uuid = uuid.uuid1()
        self._conn = MongoConn(config=MONGODB_CONFIG)
        self._book_coll = self._conn.get_coll("book_coll")
        self._beat_coll = self._conn.get_coll("beat_coll")
        self._register()
        self.result = None

    def _register(self):
        self._book_coll.insert(dict(uuid=self.uuid, name=self.name, create_time=datetime.datetime.now(), info=None))
        self._beat_coll.insert(dict(uuid=self.uuid, name=self.name, beat_time=datetime.datetime.now()))

    def _beat(self):
        self._beat_coll.update(dict(uuid=self.uuid), {"$set": {"beat_time": datetime.datetime.now()}})

    def run(self):
        print("Fetcher {0} {1} Start".format(self.name, self.uuid))
        self.prepare()
        while True:
            try:
                # print("Fetcher {0} {1} is Running".format(self.name, self.uuid))
                self.work()
                self._beat()
                if self.on_tick:
                    self.on_tick()
            except ExitSignal:
                print("Fetcher {0} {1} is Exiting".format(self.name, self.uuid))
                return self.result
            except:
                self.exception()

    def run_test(self):
        self.prepare()
        while True:
            try:
                # print("Fetcher {0} {1} is Running".format(self.name, self.uuid))
                self.work()
                self._beat()
                if self.on_tick:
                    self.on_tick()
            except ExitSignal:
                print("Fetcher {0} {1} is Exiting".format(self.name, self.uuid))
                return self.result

    def work(self):
        pass

    def prepare(self):
        pass

    def exception(self):
        pass

    def on_tick(self):
        # 每次循坏结束时候调用
        pass


def create_new_fetcher(fetcher_name, prepare_method, work_method, exception_method, tick_method=None):
    new_fetcher = type(fetcher_name, (Fetcher,),
                       dict(work=work_method, prepare=prepare_method, exception=exception_method, name=fetcher_name,
                            on_tick=tick_method))
    return new_fetcher
