import sys
import numpy as np
from price_stream import buy_limit_order, sell_limit_order

'''
Simple Strategy:

while True:
    if position = 0:
        if price is less than mean of the day:
            buy stock
        else:
            sell stock

    if position = 1:
        sell stock whenever price >entered_price by 3 cents

    if position = -1:
        buy stock whenever price < enetered_price by 3 cents
    
'''
class MyStrategy:
    def __init__ (self, window_size, mean_price, stagnation_threshold):
        self.position = 0
        self.profit = 0
        self.entered_price = 0

        self.window_size = window_size
        self.window_mean_buy = mean_price
        self.window_mean_sell = mean_price
        self.sum_buy = mean_price * window_size
        self.sum_sell = mean_price * window_size
        self.q_buy = [mean_price] * window_size
        self.q_sell = [mean_price] * window_size

        self.stagnation = stagnation_threshold
        self.unmoved = 0

        self.buy_price = -1
        self.sell_price = -1
        

    def should_make_trade(self, bid, ask, time):
        if not np.isnan(ask):
            self.buy_price = ask
            self.sum_buy += ask - self.q_buy.pop(0)
            self.q_buy.append(ask)
            self.window_mean_buy = self.sum_buy / self.window_size
        if not np.isnan(bid):
            self.sell_price = bid
            self.sell_price = bid
            self.sum_sell += bid - self.q_sell.pop(0)
            self.q_sell.append(bid)
            self.window_mean_sell = self.sum_sell / self.window_size
        

        if self.position == 0:
            print("CURRENT PROFIT IS: " , self.profit, " POSITION IS: ", self.position)
            
            if self.buy_price >= self.window_mean_buy:
                sell_limit_order(self.sell_price)
                print(time, " selling stock at ", self.sell_price)
                self.entered_price = self.sell_price
                self.position = -1
            else:
                buy_limit_order(self.buy_price)
                print(time, " buying stock at ", self.buy_price)
                self.entered_price = self.buy_price
                self.position = 1

        elif self.position == 1:
            if self.unmoved > self.stagnation and self.sell_price > self.entered_price:
                sell_limit_order(self.sell_price)
                print(time, "sell begrudgingly to flatten for ", self.sell_price)
                self.unmoved = -1
                self.position = 0
                self.profit += self.sell_price - self.entered_price

            if self.sell_price - self.entered_price > 0.2:
                sell_limit_order(self.sell_price)
                print(time, " sell to flatten for ", self.sell_price)
                self.unmoved = -1
                self.position = 0
                self.profit += self.sell_price - self.entered_price

        else:
            if self.unmoved > self.stagnation and self.buy_price < self.entered_price:
                buy_limit_order(self.buy_price)
                print(time, "buy begrudgingly to flatten for ", self.buy_price)
                self.unmoved = -1
                self.position = 0
                self.profit += self.entered_price - self.buy_price

            if self.entered_price - self.buy_price > 0.2:
                buy_limit_order(self.buy_price)
                print(time, " buy to flatten for", self.buy_price)
                self.unmoved = -1
                self.position = 0
                self.profit += self.entered_price - self.buy_price


        self.unmoved += 1
        sys.stdout.flush()

    def test_should_make_trade(self, bid, ask, time):
        if not np.isnan(ask):
            self.buy_price = ask
            self.sum_buy += ask - self.q_buy.pop(0)
            self.q_buy.append(ask)
            self.window_mean_buy = self.sum_buy / self.window_size
        if not np.isnan(bid):
            self.sell_price = bid
            self.sell_price = bid
            self.sum_sell += bid - self.q_sell.pop(0)
            self.q_sell.append(bid)
            self.window_mean_sell = self.sum_sell / self.window_size
        

        if self.position == 0:
            print("CURRENT PROFIT IS: " , self.profit, " POSITION IS: ", self.position, " MEAN IS: ", self.window_mean_buy)
            if self.buy_price >= self.window_mean_buy:
                print(time, " selling stock at ", self.sell_price)
                self.entered_price = self.sell_price
                self.position = -1

                return -1
            else:
                print(time, " buying stock at ", self.buy_price)
                self.entered_price = self.buy_price
                self.position = 1

                return 1
        elif self.position == 1:
            if self.unmoved > self.stagnation and self.sell_price > self.entered_price:
                print(time, "sell begrudgingly to flatten for ", self.sell_price)
                self.unmoved = -1
                self.position = 0
                self.profit += self.sell_price - self.entered_price

                return -1

            if self.sell_price - self.entered_price > 0.2:
                print(time, " sell to flatten for ", self.sell_price)
                self.unmoved = -1
                self.position = 0
                self.profit += self.sell_price - self.entered_price

                return -1
        else:
            if self.unmoved > self.stagnation and self.buy_price < self.entered_price:
                print(time, "buy begrudgingly to flatten for ", self.buy_price)
                self.unmoved = -1
                self.position = 0
                self.profit += self.entered_price - self.buy_price

                return 1
            if self.entered_price - self.buy_price > 0.2:
                print(time, " buy to flatten for", self.buy_price)
                self.unmoved = -1
                self.position = 0
                self.profit += self.entered_price - self.buy_price

                return 1

        self.unmoved += 1
        return 0


