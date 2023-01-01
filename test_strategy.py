from datetime import datetime
from strategies.strategyv0 import MyStrategy

from price_stream import get_history

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import boto3
import secret_keys


class StrategyTester:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.resource(
            service_name='s3',
            region_name='us-east-2',
            aws_access_key_id=secret_keys.access_key,
            aws_secret_access_key=secret_keys.secret_key
        )

    def plot_history(self, trader: MyStrategy):
        _, candles = get_history()
        
        datetimes = []
        prices = []

        for candle in candles:
            if candle['datetime'] >= 1672151765000 and candle['datetime'] <= 1672173461000:
                datetimes.append(datetime.utcfromtimestamp(candle['datetime']/1000))
                prices.append(candle['close'])
        
        for i in range(len(prices)):
            price = float(prices[i])
            trader.should_make_trade(price, datetimes[i])
        
        print(trader.position, trader.profit)

        plt.plot(datetimes, prices, '-o')

    def run_streaming_data(self, data_frame, trader: MyStrategy, title, tk = False):
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        df=data_frame.dropna(subset=['bid_price'])

        df["time"] = df["time"].apply(lambda x: datetime.strptime(x, date_format))
        
        buyx = []
        buyy = []
        sellx = []
        selly = []

        for b_price, a_price, time in zip(df.loc[:,"bid_price"], df.loc[:,"ask_price"], df.loc[:,"time"]):
            if not np.isnan(b_price) or not np.isnan(a_price):
                choice = trader.test_should_make_trade(b_price, a_price, time)
                if choice == -1:
                    sellx.append(time)
                    selly.append(a_price)
                elif choice == 1:
                    buyx.append(time)
                    buyy.append(b_price)


        if tk:
            return (df.loc[:,"time"], df.loc[:,"bid_price"]), (buyx, buyy), (sellx, selly), trader.position, trader.profit

        print(trader.position, trader.profit)
        plt.title(title)
        plt.plot(df.loc[:,"time"], df.loc[:,"bid_price"])
        plt.scatter(buyx, buyy, color='green', linewidths=3)
        plt.scatter(sellx, selly, color='red', linewidths=3)
        plt.show()

    def run_all_data_stream(self):
        for obj in self.s3.Bucket(self.bucket_name).objects.all():
            object_key = obj.key
            csv_obj = self.s3.Bucket(self.bucket_name).Object(object_key).get()
            data = pd.read_csv(csv_obj['Body'])

            trader = MyStrategy(5000, 116.88, 1000)
            self.run_streaming_data(data, trader, object_key)

    def run_single_data_stream(self, filename):
        csv_obj = self.s3.Bucket(self.bucket_name).Object(filename).get()
        data = pd.read_csv(csv_obj['Body'])

        trader = MyStrategy(5000, 117.345, 1000)
        self.run_streaming_data(data, trader, filename)

    def tk_run_single_data_stream(self, filename):
        csv_obj = self.s3.Bucket(self.bucket_name).Object(filename).get()
        data = pd.read_csv(csv_obj['Body'])

        trader = MyStrategy(5000, 117.345, 1000)
        return self.run_streaming_data(data, trader, filename, True)
