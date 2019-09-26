import sys, traceback

get_scriptname = lambda: sys.argv[0]
get_args = lambda: sys.argv[1:]

str2bytes = lambda s: bytes(s, encoding="utf8")
bytes2str = lambda b: str(b, encoding="utf8")
get_exception_info = lambda e: "\n-->Exception Content:" + str(e) + "\n-->Exception Trace:\n" + traceback.format_exc()
if __name__ == "__main__":
    print(get_args())
