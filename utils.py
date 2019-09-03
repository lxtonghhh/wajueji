import datetime

# x->2019年9月2日 09:56 GMT
GMT_to_local = lambda x: datetime.datetime.strptime(x, '%Y年%m月%d日 %H:%M %Z') + datetime.timedelta(hours=8)
time_to_str = lambda date: date.strftime("%Y-%m-%d %H:%M:%S")
if __name__ == "__main__":
    print(time_to_str(datetime.datetime.now()))
