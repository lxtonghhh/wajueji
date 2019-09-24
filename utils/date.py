#处理日期
import datetime

# x->2019年9月2日 09:56 GMT
GMT_to_local = lambda x: datetime.datetime.strptime(x, '%Y年%m月%d日 %H:%M %Z') + datetime.timedelta(hours=8)
time_to_str = lambda date: date.strftime("%Y-%m-%d %H:%M:%S")
get_year = lambda: datetime.datetime.today().year
get_month = lambda: datetime.datetime.today().month
get_day = lambda: datetime.datetime.today().day
get_hour = lambda: datetime.datetime.today().hour
get_minute = lambda: datetime.datetime.today().minute
get_second = lambda: datetime.datetime.today().second

if __name__ == "__main__":
    pass
