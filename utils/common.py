import sys, traceback
from functools import reduce

get_scriptname = lambda: sys.argv[0]
get_args = lambda: sys.argv[1:]

str2bytes = lambda s: bytes(s, encoding="utf8")
bytes2str = lambda b: str(b, encoding="utf8")
get_exception_info = lambda e: "\n-->Exception Content:" + str(e) + "\n-->Exception Trace:\n" + traceback.format_exc()

#t = [(1, "age",4), (2, "name",5), (3, "gen",6)] -->['1-age-4', '2-name-5', '3-gen-6']
tuples_to_str_list = lambda t: [reduce(lambda x, y: str(x) + "-" + str(y), i) for i in t]
if __name__ == "__main__":
    t1 = (1, "age",3)
    s = reduce(lambda x, y: str(x) + "-" + str(y), t1)
    print(s)
    t = [(1, "age",4), (2, "name",5), (3, "gen",6)]
    print(tuples_to_str_list(t))
