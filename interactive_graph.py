import matplotlib.pyplot as plt
import numpy as np

def get_closest(arr, k):
    idx = (np.abs(arr - k)).argmin()
    return idx

class StudyPlot():
    def __init__(self, x, y, span):
        self.x = np.array(x)
        self.y = np.array(y)
        self.span = span
        self.fig, self.ax = plt.subplots()

        self.pointer = None
        self.main_line = None
        self.left_line = None
        self.right_line = None
        
        self.left_span = None
        self.right_span = None

        self.connect_handlers()

    def hover(self, event):
        if event.inaxes == self.ax:
            closest = get_closest(self.x, event.xdata)

            if self.main_line:
                self.main_line.remove()
            if self.right_line:
                self.right_line.remove()
            if self.left_line:
                self.left_line.remove()
            if self.left_span:
                self.left_span.remove()
            if self.right_span:
                self.right_span.remove()
            if self.pointer:
                self.pointer.remove()

            self.main_line = self.ax.axvline(x = self.x[closest], color = 'r')

            if closest - self.span >=0:
                self.left_line = self.ax.axvline(x = self.x[closest-self.span], color = 'r')
                self.left_span = self.ax.axvspan(closest-self.span, closest, alpha=0.5, color='red')
            else:
                self.left_line = None
                self.left_span = self.ax.axvspan(0, closest, alpha=0.5, color='red')
            if closest + self.span <len(self.y):
                self.right_line = self.ax.axvline(x = self.x[closest+self.span], color = 'r')
                self.right_span = self.ax.axvspan(closest, closest+self.span, alpha=0.5, color='red')
            else:
                self.right_line = None
                self.right_span = self.ax.axvspan(closest, len(self.y), alpha=0.5, color='red')

            self.pointer = self.ax.scatter(x=self.x[closest], y=self.y[closest], color='black', linewidths=3)
            self.fig.canvas.draw()

    def connect_handlers(self):
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
    
    def plot(self):
        self.ax.plot(self.x, self.y)

        plt.show()
        

data = np.load("price_data.npz")["arr_0"]

study = StudyPlot(np.arange(len(data)),data, 1000)

study.plot()





