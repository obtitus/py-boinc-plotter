#!/usr/bin/env python

# Standard python
import calendar
from collections import namedtuple
import logging
logger = logging.getLogger('boinc.jobLog')
# Non standard
# Project imports
from project import Project
from importMatplotlib import *
from util import diffMonths
import task

def createFromFilename(cls, filename, limitMonths=None, label=''):
    """ Returns a JobLog instance from a given filename
    """
    with open(filename, 'r') as f:
        return createFromFilehandle(cls, f, limitMonths=limitMonths, label=label)

def createFromFilehandle(cls, f, limitMonths=None, label=''):
    """ Returns a JobLog instance from a given filehandle
    ue - estimated_runtime_uncorrected
    ct - final_cpu_time, cpu time to finish
    fe - rsc_fpops_est, estimated flops
    et - final_elapsed_time, clock time to finish
    """
    tasks = cls(label=label)
    now = datetime.datetime.now()
    for line in f:
        t = task.Task_jobLog.createFromJobLog(line)
        if limitMonths == None or diffMonths(t.time, now) < limitMonths:
            tasks.append(t)
    return tasks

class JobLog(list):
    """
    List of Tasks, where additional information is available for tasks still on the web or 'ready to report'.
    Focus is on plotting as either points or bars
    """
    def __init__(self, label, **kwargs):
        super(JobLog, self).__init__(**kwargs)
        self.label = label

    @property
    def time(self):
        return [task.time for task in self]
    @property
    def ue(self):
        return [task.estimated_runtime_uncorrected for task in self]
    @property
    def ct(self):
        return [task.final_elapsed_time for task in self]
    @property
    def fe(self):
        return [task.rsc_fpops_est for task in self]
    @property
    def et(self):
        return [task.final_elapsed_time for task in self]
    @property
    def names(self):
        return [task.name for task in self]

    def plot(self, fig):
        """ Plots the job_log to the given figure instance
        """
        N = 4                               # Number of subplots
        axes = list()
        ax1 = fig.add_subplot(N, 1, 1)
        for ix in range(N):
            if ix != 3:
                ax = fig.add_subplot(N, 1, ix+1, sharey=ax1)
            else:
                ax = fig.add_subplot(N, 1, ix+1)
            barPlotter = BarPlotter(ax)
            axes.append(barPlotter)

        # Plot datapoints and bars, make sure the same colors are used.
        color = self.plot_datapoints(axes)
        if color != []:
            self.plot_hist_day(color, axes)

        self.formatAxis(axes)

    def formatXAxis(self, ax):
        dayFormat(ax)

    def formatAxis(self, axes):
        for ax in axes:
            self.formatXAxis(ax)

        leg = axes[3].legend()
        if leg is not None:
            leg.draggable()

        ylabels = ['Estimated time', 'Final CPU time', 'Final clock time', 'Tflops']
        for ix, ax in enumerate(axes):
            ax.set_xlabel('Date')
            if ix != len(axes)-1: # last axes
                ax.yaxis.set_major_formatter(formatter_timedelta)
                plt.setp(ax.get_xticklabels(), visible=False)

            ax.set_ylabel(ylabels[ix])

    def plot_datapoints(self, axes):
        """
        Let each datapoint be a single dot
        """
        time = self.time
        if len(time) == 0:
            return []

        kwargs = dict(ls='none', marker='o')
        for ix, data in enumerate([self.ue, self.ct, self.et, self.fe]):
            if ix == 3:
                data = np.array(data)/1e12
            line = axes[ix].plot(time, data, **kwargs)

        color = line[0].get_color()

        return color

    def plot_hist_day(self, color, axes):
        """
        Create a single bar for each day
        """
        time, ue, ct, fe, name, et = self.time, self.ue, self.ct, self.fe, self.names, self.et

        if len(time) == 0: return ;         # make sure we actually have data to work with

        currentDay = time[0]#plt.num2date(time[0])
        cumulative = np.zeros(4) # [ue, ct, et, fe]
        #cumulative = np.zeros(3) # [ue, ct, et]

        def myBarPlot(currentDay, cumulative, **kwargs):
            d = currentDay.replace(hour=0, minute=0, second=0, microsecond=0) # Reset to 0:00:00 this day for alignment of bars
            x = plt.date2num(d)
            # Plot bars
            kwargs['width'] = 1
            kwargs['alpha'] = 0.5
            kwargs['color'] = color
            axes[0].bar(x, cumulative[0], **kwargs)
            axes[1].bar(x, cumulative[1], **kwargs)
            axes[2].bar(x, cumulative[2], **kwargs)
            axes[3].bar(x, cumulative[3]/1e12, **kwargs)

        for ix in range(len(time)):
            # If new day, plot and null out cumulative
            if currentDay.day != time[ix].day:
                myBarPlot(currentDay, cumulative)
                # Prepare for next loop
                currentDay = time[ix]
                cumulative = np.zeros(len(cumulative))

            # Add events associated with time[ix]
            cumulative[0] += ue[ix]
            cumulative[1] += ct[ix]
            cumulative[2] += et[ix]
            cumulative[3] += fe[ix]

        # plot last day
        myBarPlot(time[-1], cumulative, label=self.label)

class JobLog_Months(JobLog):
    """ JobLog focus is on single events summed up to one day, 
    this class focuses on days being summed to months
    """
    def plot_datapoints(self, axes):
        color = axes[0]._get_lines.color_cycle.next()
        JobLog.plot_hist_day(self, color, axes)
        return color

    def plot_hist_day(self, color, axes):
        """ Replaces hist_day with hist_month
        """
        time, ue, ct, fe, name, et = self.time, self.ue, self.ct, self.fe, self.names, self.et

        if len(time) == 0: return ;         # make sure we actually have data to work with

        currentDay = time[0]
        cumulative = np.zeros(4) # [ue, ct, et, fe]

        def myBarPlot(currentDay, cumulative, **kwargs):
            d = currentDay.replace(day=1, hour=0, minute=0, second=1, microsecond=0) # Reset to 0:00:00 this month for alignment of bars
            x = plt.date2num(d)
            # Plot bars
            _, daysInMonth = calendar.monthrange(currentDay.year,
                                                 currentDay.month)
            kwargs['width'] = daysInMonth
            kwargs['alpha'] = 0.5
            kwargs['color'] = color
            axes[0].bar(x, cumulative[0], **kwargs)
            axes[1].bar(x, cumulative[1], **kwargs)
            axes[2].bar(x, cumulative[2], **kwargs)
            axes[3].bar(x, cumulative[3]/1e12, **kwargs)

        for ix in range(len(time)):
            # If new month, plot and null out cumulative
            if currentDay.month != time[ix].month:
                myBarPlot(currentDay, cumulative)
                # Prepare for next loop
                currentDay = time[ix]
                cumulative = np.zeros(len(cumulative))

            # Add events associated with time[ix]
            cumulative[0] += ue[ix]
            cumulative[1] += ct[ix]
            cumulative[2] += et[ix]
            cumulative[3] += fe[ix]

        # plot last month
        myBarPlot(time[-1], cumulative)
        

    def formatXAxis(self, ax):
        dayFormat(ax, month=True)

class BarPlotter(object):
    # Bar plotter that remembers bottom
    # and automatically plots bars stacked in stead of on top of each other
    # Assumes that bar is called with only a single bar at a time
    def __init__(self, ax):
        self.ax = ax
        if not(hasattr(self.ax, 'bottom')):
            self.ax.bottom = dict()     # key is x coordinate and value is height

    def clear(self):
        print 'clearing', self.ax.bottom
        self.ax.bottom = dict()
        
    def __getattr__(self, name):
        """ Redirect to axes
        """
        return self.ax.__getattribute__(name)

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

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    import util
    
    _, _, BOINC_DIR = config.set_globals()
    fig1 = plt.figure()
    fig2 = plt.figure()
    for url, filename in util.getLocalFiles(BOINC_DIR, 'job_log', '.txt'):
        project = Project(url)
        tasks = createFromFilename(JobLog, filename, label=project.name_short, limitMonths=1)
        tasks.plot(fig=fig1)

        tasks = createFromFilename(JobLog_Months, filename, label=project.name_short, limitMonths=12)
        tasks.plot(fig=fig2)

    raw_input('=== Press enter to exit ===\n')
