# 处理数据
import math, json


# ["sh601000", "2019-09-21 12:19:00", 8.75]

def head(l, key=lambda x: x[2], n=10):
    return sorted(l, key=key, reverse=True)[0:n]


def tail(l, key=lambda x: x[2], n=10):
    return sorted(l, key=key)[0:n]


def divide(l, key=lambda x: x[2], step=1, length=16):
    # 从[0,16)分成16个数组
    res = [[] for _ in range(length)]
    for i in l:
        group = int(key(i) // step)
        res[group].append(i)
    for i in range(len(res)):
        print(i, "->", len(res[i]))
    return res


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
    from constant import ROOT_DIR
    print(ROOT_DIR)
    with open(ROOT_DIR+"output/9_24_14_86400.json", "r", encoding="utf-8") as f:
        obj = json.load(f)
        nobj = divide(obj)
        print([share[0] for share in nobj[14]])
