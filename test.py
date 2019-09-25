import os, time, datetime, json


def f(name, age):
    print(name, age)


def wrapper(func, **kwargs):
    func(**kwargs)


if __name__ == "__main__":
    wrapper(func=f, **dict(name="liu", age=21))
    exit(1)
    l = [('sh600197', 14.0), ('sh601800', 13.75), ('sz300042', 14.0), ('sh601231', 14.0), ('sh600237', 14.0),
         ('sz300365', 13.75), ('sh600557', 13.75), ('sh600720', 14.0), ('sh600516', 14.0)]

    s = [i[0] for i in l]
    print(s)
    with open("local/share.json", "r", encoding="utf-8") as f:
        obj = json.load(f)
        print()
