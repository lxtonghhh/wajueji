import sys

get_scriptname = lambda: sys.argv[0]
get_args = lambda: sys.argv[1:]

if __name__ == "__main__":
    print(get_args())
