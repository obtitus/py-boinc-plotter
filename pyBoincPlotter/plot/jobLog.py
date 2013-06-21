# Standard python
from collections import namedtuple
# Non standard
# Project imports
from importMatplotlib import *

class JobLog(namedtuple('JobLog', dict(time=list(), ue=list(), ct=list(), fe=list(), et=list(), names=list()))):
    def plot(self):
        self.N = 4                               # Number of subplots
        time, ue, ct, fe, name, et = plt.date2num(self.time), self.ue, self.ct, self.fe, self.names, self.et
        self.plot_datapoints(time, ue, ct, fe, name, et)
        self.plot_hist_day(time, ue, ct, fe, name, et)

    def plot_datapoints(self, time, ue, ct, fe, name, et):
        ix = 1                              # current subplot
        kwargs = dict(ls='none', marker='o')

        ax1 = fig.add_subplot(self.N, 1, ix); ix += 1
        l1 = ax1.plot(time, ue, label=projectName, **kwargs)
        ax1.set_ylabel('Estimated time')    # uncorrected

        ax2 = fig.add_subplot(self.N, 1, ix, sharex=ax1, sharey=ax1); ix += 1
        l2 = ax2.plot(time, ct, label=projectName, **kwargs)
        ax2.set_ylabel('Final CPU time')

        ax3 = fig.add_subplot(self.N, 1, ix, sharex=ax1, sharey=ax1); ix += 1    
        l3 = ax3.plot(time, et, label=projectName, **kwargs)    
        ax3.set_ylabel('Final clock time')

        ax4 = fig.add_subplot(self.N, 1, ix, sharex=ax1); ix += 1
        l4 = ax4.plot(time, np.array(fe)/1e12, label=projectName, **kwargs)
        ax4.set_ylabel('Tflops')

        color = [l1[0].get_color(), l2[0].get_color(), l3[0].get_color(), l4[0].get_color()]

        ax4.legend().draggable()

        for ax in fig.axes:
            ax.set_xlabel('Date')
        for ax in [ax1, ax2, ax3]:
            plt.setp(ax.get_xticklabels(), visible=False)
            ax1.yaxis.set_major_formatter(formatter_timedelta)

    def plot_hist_day(self, time, ue, ct, fe, name, et):
        # Now for the histogram part
        if len(time) == 0: return ;         # make sure we actually have data to work with

        currentDay = plt.num2date(time[0])
        cumulative = np.zeros(4) # [ue, ct, et, fe]
        #cumulative = np.zeros(3) # [ue, ct, et]

        b1 = BarPlotter(ax1)
        b2 = BarPlotter(ax2)
        b3 = BarPlotter(ax3)
        b4 = BarPlotter(ax4)
        def myBarPlot(currentDay, cumulative):
            d = currentDay.replace(hour=0, minute=0, second=0, microsecond=0) # Reset to 0:00:00 this day for alignment of bars
            x = plt.date2num(d)
            # Plot bars
            b1.bar(x, cumulative[0], width=1, alpha=0.5, color=color[0])
            b2.bar(x, cumulative[1], width=1, alpha=0.5, color=color[1])
            b3.bar(x, cumulative[2], width=1, alpha=0.5, color=color[2])
            b4.bar(x, cumulative[3]/1e12, width=1, alpha=0.5, color=color[3])

        for ix in range(len(time)):
            # If new day, plot and null out cumulative
            if currentDay.day != plt.num2date(time[ix]).day:
                myBarPlot(currentDay, cumulative)
                # Prepare for next loop
                currentDay = plt.num2date(time[ix])
                cumulative = np.zeros(len(cumulative))

            # Add events associated with time[ix]
            cumulative[0] += ue[ix]
            cumulative[1] += ct[ix]
            cumulative[2] += et[ix]
            cumulative[3] += fe[ix]

        # plot last day
        myBarPlot(plt.num2date(time[-1]), cumulative)
        for ax in fig.axes:
            dayFormat(ax)

        return color[0]

class BarPlotter(object):
    # Bar plotter that remembers bottom
    # and automatically plots bars stacked in stead of on top of each other
    # Assumes that bar is called with only a single bar at a time
    def __init__(self, ax):
        self.ax = ax
        if not(hasattr(self.ax, 'bottom')):
            self.ax.bottom = dict()     # key is x coordinate and value is height
        
    def bar(self, x, *args, **kwargs):
        # Find previous (if any)
        try:
            b = self.ax.bottom[x]
        except KeyError:
            b = 0
        kwargs['bottom'] = b
        # Plot
        rect = self.ax.bar(x, *args, **kwargs)[0]

        # Remember
        x, y = rect.get_xy()
        self.ax.bottom[x] = y + rect.get_height()
        return b

    def plot(self, *args, **kwargs):
        self.ax.plot(*args, **kwargs)
