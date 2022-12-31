

'''
Simple Strategy:

if we are increasing past a certain length, 
    and get an opposite trend, buy/sell because we estimate
    an opposite trend occuring
    
'''
class PeakAndValleyStrategy:
    def __init__ (self, threshold):
        self.streak_dir = 0
        self.streak_len = 0
        self.prev_price = -1
        self.threshold = threshold
        self.profit = 0
        self.position = 0

    def should_make_trade(self, price, time):
        if self.prev_price != -1:
            if self.streak_dir == 1:
                if price >= self.prev_price:
                    self.streak_len += 1

                else:
                    if self.streak_len >= self.threshold:
                        print(time, "selling stock at ", price)
                        self.position -= 1
                        self.profit += price
                    self.streak_dir = -1
                    self.streak_len = 1
            else:
                if price <= self.prev_price:
                    self.streak_len += 1
                else:
                    if self.streak_len >= self.threshold:
                        print(time, "buying stock at ", price)
                        self.position += 1
                        self.profit -= price
                    self.streak_dir = 1
                    self.streak_len = 1
        self.prev_price = price
                    







