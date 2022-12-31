from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import boto3
import secret_keys
import subprocess
import test_strategy
import tkinter as tk

s3 = boto3.resource(
        service_name='s3',
        region_name='us-east-2',
        aws_access_key_id=secret_keys.access_key,
        aws_secret_access_key=secret_keys.secret_key
    )
bucket_name = 'equities-streaming-data'

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Buy Me Dinner")
        self.createWidgets()

        self.columnconfigure(tuple(range(3)), weight=1)
        self.rowconfigure(tuple(range(2)), weight=1)

    
    def createWidgets(self):
        self.createActiveTradingFrame()

        selections = []
        for obj in s3.Bucket(bucket_name).objects.all():
            selections.append(obj.key)

        selections = tk.Variable(value=selections)
        available_datasets = tk.Listbox(self, listvariable=selections)
        available_datasets.grid(column=2, row=2, sticky="news")

        test_strat_button = tk.Button(self, text="Single ", 
                command=lambda : self.testStrategyPlot(available_datasets.get(available_datasets.curselection())))
        test_strat_button.grid(column=1, row=2)

        self.testStrategyPlot("META_12_27_22.csv")



    def testStrategyPlot(self, filename):
        datapoints, buys, sells, position, profit= test_strategy.tk_run_single_data_stream(filename)

        fig = Figure()
        plot = fig.add_subplot(111)
        
        plot.set_title(filename)
        plot.plot(datapoints[0], datapoints[1])
        plot.scatter(buys[0], buys[1], color='green', linewidths=3)
        plot.scatter(sells[0], sells[1], color='red', linewidths=3)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()

        canvas.get_tk_widget().grid(column=1, row=0, sticky="news")

        toolbarFrame = tk.Frame(self)
        toolbarFrame.grid(column=1, row=1)
        toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        strategy_log = tk.Text(self, wrap='none')
        strategy_log.insert('1.0', "position is: " + str(position) + " profit is: " + str(profit))
        strategy_log.configure(state="disable")
        strategy_log.grid(column=2, row=0, rowspan=2, sticky="news")


    def createActiveTradingFrame(self):
        def writeToLog(msg):
            numlines = int(log.index('end - 1 line').split('.')[0])
            log['state'] = 'normal'
            if numlines==24:
                log.delete(1.0, 2.0)
            if log.index('end-1c')!='1.0':
                log.insert('end', '\n')
            log.insert('end', msg)
            log['state'] = 'disabled'

        def run_market_streamer():
            popen = subprocess.Popen(["python", "market_streamer.py"], stdout=subprocess.PIPE, universal_newlines=True)
            for stdout_line in iter(popen.stdout.readline, ""):
                writeToLog(stdout_line)
            popen.stdout.close()

        tradingFrame = tk.Frame(self)
        tradingFrame.grid(column=0, row=0)

        start_trade_button = tk.Button(tradingFrame, text="start trading", command = run_market_streamer)
        start_trade_button.grid(column=0, row=0, sticky="news")

        log = tk.Text(tradingFrame, state='disabled', wrap='none')
        log.grid(column=0, row=1, sticky='news')

app = Application()
app.mainloop()