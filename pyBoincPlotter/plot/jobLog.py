# Standard python
from collections import namedtuple
# Non standard
# Project imports
from importMatplotlib import *

class JobLog(list):
    """
    List of Tasks, where additional information is available for tasks still on the web or 'ready to report'.
    Focus is on plotting as either points or bars
    """
    @staticmethod
    def createFromFilename(filename, limitDays=None):
        """ Returns a JobLog instance from a given filename
        """
        with open(filename, 'r') as f:
            return self.createFromFilehandle(f, limitDays=limitDays)

    @staticmethod
    def createFromFilehandle(f, limitDays=None):
        """ Returns a JobLog instance from a given filehandle
        ue - estimated_runtime_uncorrected
        ct - final_cpu_time, cpu time to finish
        fe - rsc_fpops_est, estimated flops
        et - final_elapsed_time, clock time to finish
        """
        tasks = JobLog()
        now = datetime.datetime.now()
        for line in f:
            t = Task_jobLog.createFromJobLog(line)
            if limitDaysToPlot == None or now - t._time < limitDays:
                tasks.append(t)
        return tasks

    def plot(self, fig):
        """ Plots the job_log to the given figure instance
        """
        N = 4                               # Number of subplots
        axes = list()
        ax1 = fig.add_subplot(N, 1, ix)
        for ix in range(N):
            ax = fig.add_subplot(N, 1, ix+1, sharex=ax1, sharey=ax1)
            barPlotter = BarPlotter(ax)
            axes.append(barPlotter)

        # Plot datapoints and bars, make sure the same colors are used.
        color = self.plot_datapoints(axes)
        self.plot_hist_day(color, axes)

    def plot_datapoints(self, axes):
        """
        Let each datapoint be a single dot
        """
        time, ue, ct, fe, name, et = self.time, self.ue, self.ct, self.fe, self.names, self.et
        ix = 1                              # current subplot
        kwargs = dict(ls='none', marker='o')

        l1 = axes[0].plot(time, ue, label=projectName, **kwargs)
        axes[0].set_ylabel('Estimated time')    # uncorrected

        l2 = axes[1].plot(time, ct, label=projectName, **kwargs)
        axes[1].set_ylabel('Final CPU time')

        l3 = axes[2].plot(time, et, label=projectName, **kwargs)    
        axes[2].set_ylabel('Final clock time')

        l4 = axes[3].plot(time, np.array(fe)/1e12, label=projectName, **kwargs)
        axes[3].set_ylabel('Tflops')

        color = [l1[0].get_color(), l2[0].get_color(), l3[0].get_color(), l4[0].get_color()]

        axes[3].legend().draggable()

        for ix, ax in enumerate(axes):
            ax.set_xlabel('Date')
            if ix == len(axes)-1: # last axes
                ax1.yaxis.set_major_formatter(formatter_timedelta)
            else:               # hide the rest
                plt.setp(ax.get_xticklabels(), visible=False)

        return color

    def plot_hist_day(self, color, axes):
        """
        Create a single bar for each day
        """
        time, ue, ct, fe, name, et = self.time, self.ue, self.ct, self.fe, self.names, self.et

        if len(time) == 0: return ;         # make sure we actually have data to work with

        currentDay = plt.num2date(time[0])
        cumulative = np.zeros(4) # [ue, ct, et, fe]
        #cumulative = np.zeros(3) # [ue, ct, et]

        def myBarPlot(currentDay, cumulative):
            d = currentDay.replace(hour=0, minute=0, second=0, microsecond=0) # Reset to 0:00:00 this day for alignment of bars
            x = plt.date2num(d)
            # Plot bars
            axes[0].bar(x, cumulative[0], width=1, alpha=0.5, color=color[0])
            axes[1].bar(x, cumulative[1], width=1, alpha=0.5, color=color[1])
            axes[2].bar(x, cumulative[2], width=1, alpha=0.5, color=color[2])
            axes[3].bar(x, cumulative[3]/1e12, width=1, alpha=0.5, color=color[3])

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
        
    def __getattr__(self, name):
        """ Redirect to axes
        """
        return self.ax.__getattr__(name)

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

    # def plot(self, *args, **kwargs):
    #     self.ax.plot(*args, **kwargs)
