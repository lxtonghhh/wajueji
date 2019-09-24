import json


def my_time_strategy(tick, data, base_price, n=0.07):
    """
    # 最高点或者最低点大于成本价n个点卖出 否则一直持仓至周期结束
    :param tick: 当前tick_idx
    :param data: list [
            [(share1_open_tick1, high1, low1, close1),(share1_open_tick2, high2, low2, close2),...],
            [(share2_open_tick1, high1, low1, close1),(share2_open_tick2, high2, low2, close2),...],
            [(share3_open_tick1, high1, low1, close1),(share3_open_tick2, high2, low2, close2),...],
            ]
    :param base_price: 对应data中标的的建仓价格
    :return: decisions: [[share_idx,buy_or_sell(0 sell, 1 buy),amount,price]]
    """
    decisions = []
    for share in range(len(data)):
        if (data[share][tick][1] - base_price[share]) / base_price[share] > n:
            # 盈利卖出
            decisions.append([share, 0, 1, data[share][tick][1]])
        elif (data[share][tick][1] - base_price[share]) / base_price[share] < -n:
            # 亏损卖出
            decisions.append([share, 0, 1, data[share][tick][1]])
        else:
            pass
    return decisions


def prepare():
    with open("output.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


class Agent(object):
    def __init__(self, data, time_strategy=my_time_strategy, share_strategy=None, ):
        """
        agent根据交易策略在一组tick中进行模拟交易
        计算收益率 最大回撤
        :param data -> dict
        info:dict {
        size:int数据的tick大小(5 15 30 60)间隔分钟,
        start:date开始时间,
        end:date结束时间,
        map:list标的名称和代码映射
            [{"name":...,"code":...},{"name":...,"code":...}],
        content:list [
            [(share1_open_tick1, high1, low1, close1),(share1_open_tick2, high2, low2, close2),...],
            [(share2_open_tick1, high1, low1, close1),(share2_open_tick2, high2, low2, close2),...],
            [(share3_open_tick1, high1, low1, close1),(share3_open_tick2, high2, low2, close2),...],
            ]
        :return:
        """
        self.tick_size = data["info"]["size"]
        self.tick_start = data["info"]["start"]
        self.tick_end = data["info"]["end"]
        self.share_map = data["info"]["map"]

        self.data = data["content"]

        self.tick_num = len(self.data[0])
        self.share_num = len(self.data)  # 当前self.data中标的
        self.share_total_num = len(self.data)  # 所有参与的标的 包含被清除的
        # 建仓价格 默认为第一个tick的open
        self.base_price = [share[0][0] for share in self.data]
        # 建仓总额
        self.base_amount = sum(self.base_price)
        # 是否持仓状态
        self.is_holding = [True for share in self.data]
        # 最大回撤
        self.max_drawback = 0
        # 计算胜率
        self.win, self.lose = 0, 0
        # 计算累计盈利
        self.total_profit = 0

        # 交易记录
        self.log = []
        # 每次tick的回撤记录
        self.drawbacks = []

        # 选股策略
        self.share_strategy = share_strategy
        # 择时策略
        self.time_strategy = time_strategy

    def tick_make_decision(self, tick):
        """
        判断该tick是否交易 交易量
        :param tick: 当前tick_idx
        :return:

        """
        tick = tick
        data, _tmp2raw, _tmp_c = [], {}, 0
        base_price = []
        # 制作正在持有的数据集

        for i in range(self.share_num):
            if self.is_holding[i] is True:
                base_price.append(self.base_price[i])
                data.append(self.data[i])
                _tmp2raw[_tmp_c] = i
                _tmp_c += 1
            else:
                pass
        _decisions = self.time_strategy(tick, data, base_price)
        # decision->[[share_idx,buy_or_sell(0 sell, 1 buy),amount,price]]
        # 根据map还原idx
        for d in _decisions:
            d[0] = _tmp2raw[d[0]]
        return _decisions

    def tick_execute(self, tick, decisions):
        """
        执行交易决定 并记录
        :param tick: 当前tick_idx
        :param decisions: [[share_idx,buy_or_sell(0 sell, 1 buy),amount,price]]
        :return:
        """
        # 默认每个决定都能执行
        for decision in decisions:
            # 卖出执行
            # 计算收益亏损
            share, buy_or_sell, amount, deal_price = decision
            profit = round((deal_price - self.base_price[share]) / self.base_price[share], 4)
            if profit > 0:
                print("-->在第", str(tick), "个TICK 盈利卖出", self.share_map[share]["name"], "卖出价格: ", deal_price,
                      "收益： ", profit)
                self.win += 1
                self.is_holding[share] = False
            else:
                print("-->在第", str(tick), "个TICK 亏损卖出", self.share_map[share]["name"], "卖出价格: ", deal_price,
                      "收益： ", profit)
                self.lose += 1
                self.is_holding[share] = False

            self.log.append(
                dict(share=self.share_map[share], buy_or_sell=buy_or_sell, amount=amount, deal_price=deal_price,
                     profit=profit))
            self.total_profit += deal_price - self.base_price[share]

    def tick_reflection(self, tick):
        """
        每次tick的反思总结
        计算当前tick当前组合的最大回撤
        :param tick: 当前tick_idx
        :return:
        """
        drawback = 0
        for i in range(self.share_num):
            if self.is_holding[i] is True:
                drawback += self.base_price[i] - self.data[i][tick][2]  # 买入价-当前tick最低价
            else:
                pass
        drawback = round(drawback / self.base_amount, 4)
        #print("本TICK回撤: ", drawback)
        self.drawbacks.append(drawback)

        # 更新最大回撤
        self.max_drawback = drawback if drawback > self.max_drawback else self.max_drawback

    def tick_summary(self):
        """
        最终的反思总结
        计算胜率和最终持仓
        :return:
        """
        print("-->最大回撤", self.max_drawback)

        # 计算最终没有卖出的标的
        for share in range(self.share_num):
            if self.is_holding[share] is True:
                profit = round((self.data[share][-1][3] - self.base_price[share]) / self.base_price[share], 4)
                print("-->当前持仓 ", self.share_map[share]["name"], " 当前收益： ", profit)
                if profit >= 0.02:
                    self.win += 1
                elif profit <= -0.02:
                    self.lose += 1

        print("-->胜率: ", round(float(self.win) / self.share_total_num, 4))
        print("-->败率: ", round(float(self.lose) / self.share_total_num, 4))

    def work(self):
        for tick in range(self.tick_num):
            # 遍历每个tick 获得即将执行的交易
            decisions = self.tick_make_decision(tick)
            self.tick_execute(tick, decisions)
            self.tick_reflection(tick)
        self.tick_summary()


if __name__ == "__main__":
    data = prepare()
    a = Agent(data)
    a.work()
