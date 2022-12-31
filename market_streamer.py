from price_stream import read_stream, get_market_hours
from datetime import date, datetime
from strategies.strategyv0 import MyStrategy
from postprocess_times import post_process_csv

import asyncio
import boto3
import csv
import secret_keys
import sys

class MarketStreamer:
    def __init__(self):
        filename = date.today().strftime("%m_%d_%y") + ".csv"
        self.f_meta = open('META_' + filename, 'w')
        self.f_aapl = open('AAPL_' + filename, 'w')
        self.writer_meta = csv.writer(self.f_meta)
        self.writer_aapl = csv.writer(self.f_aapl)
        self.q = []
        self.updated = False
        self.trader = MyStrategy(5000, 120.26, 1000)

    def handle_equities_quotes(self, message):
        time = datetime.utcfromtimestamp(message["timestamp"]/1000)
        if "content" in message:
            for content in message["content"]:
                symbol = content["key"]
                print("symbol")
                bid_price = content["BID_PRICE"] if "BID_PRICE" in content else None
                ask_price = content["ASK_PRICE"] if "ASK_PRICE" in content else None

                if bid_price != None or ask_price != None:
                    self.writer.writerow([symbol, time, bid_price, ask_price]) 
                    self.f.flush()
                    self.q.append((bid_price, ask_price))
                    with self.cv:
                        self.q.append((bid_price, ask_price))
                        self.updated = True
                        self.cv.notify()
                    print(time, "BID_PRICE = " + str(bid_price), 
                           "ASK_PRICE = " + str(ask_price))
    
    def trading_equities_handler(self, message):
        time = datetime.utcfromtimestamp(message["timestamp"]/1000)
        sys.stdout.flush()
        if "content" in message:
            for content in message["content"]:
                symbol = content["key"]
                bid_price = content["BID_PRICE"] if "BID_PRICE" in content else None
                ask_price = content["ASK_PRICE"] if "ASK_PRICE" in content else None
                total_volume = content["TOTAL_VOLUME"] if "TOTAL_VOLUME" in content else None
                open_price = content["OPEN_PRICE"] if "OPEN_PRICE" in content else None
                quote_time = content["QUOTE_TIME"] if "QUOTE_TIME" in content else None

                if symbol == 'META':
                    self.writer_meta.writerow([time, bid_price, ask_price, total_volume, open_price, quote_time]) 
                    self.f_meta.flush()

                    if bid_price != None or ask_price != None:
                        self.trader.should_make_trade(bid_price, ask_price, time)
                        self.q.append((time, bid_price, ask_price))

                if symbol == 'AAPL':
                    self.writer_aapl.writerow([time, bid_price, ask_price, total_volume, open_price, quote_time]) 
                    self.f_aapl.flush()

    def stream_data(self):
        print("market hours: ", get_market_hours())
        sys.stdout.flush()
        asyncio.run(read_stream(self.trading_equities_handler, get_market_hours()))

        self.f_meta.close()
        self.f_aapl.close()

        s3 = boto3.resource(
            service_name='s3',
            region_name='us-east-2',
            aws_access_key_id=secret_keys.access_key,
            aws_secret_access_key=secret_keys.secret_key
        )

        post_process_csv(self.f_meta.name)
        post_process_csv(self.f_aapl.name)

        s3.Bucket('equities-streaming-data').upload_file(Filename=self.f_meta.name, Key=self.f_meta.name)
        s3.Bucket('equities-streaming-data').upload_file(Filename=self.f_aapl.name, Key=self.f_aapl.name)

        print("bucket_uploaded")
        sys.stdout.flush()



if __name__ == "__main__":
    streamer = MarketStreamer()
    streamer.stream_data()




