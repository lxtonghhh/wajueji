from fetchers.HistoryTick import scan_tick_data

MA_DICT = {5: "5", 10: "10", 15: "15", 20: "20", 25: "25", }
INTERVAL_DICT = {5: "5", 15: "15", 30: "30", 60: "60", }  # 间隔分钟
# 每天交易4小时 一天有48个5分钟数据 16个15分钟数据 8个30分钟数据 4个60分钟数据 datalen最大限制为200
PARAMS_50_day_by_60m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[60], datalen=4 * 50)
PARAMS_10_day_by_15m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[15], datalen=16 * 10)
PARAMS_4_day_by_5m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[5], datalen=48 * 4)
PARAMS_3_day_by_5m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[5], datalen=48 * 3)
PARAMS_2_day_by_5m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[5], datalen=48 * 2)
PARAMS_1_day_by_5m = dict(MA=MA_DICT[5], interval=INTERVAL_DICT[5], datalen=48 * 1)


def start():
    # 所有股票 15分钟10天tick 存入数据库中
    scan_tick_data(output=None, is_test=False, is_all=True, params=PARAMS_10_day_by_15m, is_save=True)
