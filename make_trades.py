from matplotlib.animation import FuncAnimation
from datetime import datetime

import matplotlib.pyplot as plt
import asyncio
import json
import httpx
import csv
import pandas as pd
import os
import time

class MarketTrader:
    def __init__(self, filename):
        self.filename = filename

    def run_charts(self):

        def animate(i):
            data = pd.read_csv(self.filename)
            print(data)
            x = data[1]
            y1 = data[2]
            y2 = data[3]

            plt.cla()

            plt.plot(x, y1, label="bid_price")
            plt.plot(x, y2, label="ask_pric")
            
            plt.title(data[0])
            plt.tight_layout()

        ani = FuncAnimation(plt.gcf(), animate, interval=500)
        plt.tight_layout()
        plt.show()

trader = MarketTrader("live_data.csv")

#trader.run_charts()

def follow(thefile):
    '''generator function that yields new lines in a file
    '''
    # seek the end of the file
    thefile.seek(0, os.SEEK_END)
    
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()
        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue

        yield line


logfile = open("live_data.csv","r")
loglines = follow(logfile)
# iterate over the generator
for line in loglines:
    print(line)


