import datetime


class Portfolio(object):
    def __init__(self, name, datas, date=datetime.datetime.now()):
        """

        :param datas:
        [[code,name,price,ratio]](代码，名称，买入价，持仓额 默认为1 0表示清仓)
        :param date:
        """
        self.name = name
        self._date = date  # 建仓时间
        self.shares = datas
        self.history = []  # 交易记录[(tick_id,is_sell,buy_price,sell_price,profit]
        self._profit = 0

    def sell(self, i, tick_id, sell_price, sell_ratio=1, ):
        if self.shares[i][3] - sell_ratio >= 0:
            self.shares[i][3] = 0
            self.history.append(
                (tick_id, True, self.shares[i][2], sell_price, (sell_price - self.shares[i][2]) / self.shares[i][2]))
            self._profit += (sell_price - self.shares[i][2]) * sell_ratio
        else:
            pass

    @property
    def profit(self):
        print("***组合_" + self.name + "当前收益: " + self._profit)
        return self._profit
