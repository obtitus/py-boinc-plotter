#!/usr/bin/env python
# This file is part of the py-boinc-plotter,
# which provides parsing and plotting of boinc statistics and
# badge information.
# Copyright (C) 2013 obtitus@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# END LICENCE

# Standard python
import calendar
from collections import namedtuple
import logging
logger = logging.getLogger('boinc.plot.jobLog')
# Non standard
# Project imports
import projectColors
try:
    from .. import task
    from ..project import Project
    from .. import util
except ValueError:
    import task
    from project import Project
    import util

from importMatplotlib import *

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
        if limitMonths == None or util.diffMonths(t.time, now) < limitMonths:
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

        self._time = list()#self.createArray('time')
        self._ue = self.createArray('estimated_runtime_uncorrected')
        self._ct = self.createArray('final_cpu_time')
        self._fe = self.createArray('rsc_fpops_est')
        self._et = self.createArray('final_elapsed_time')
        self._names = list()

    def createArray(self, attr):
        ret = np.zeros(len(self))
        for ix, item in enumerate(self):
            value = getattr(item, attr)
            ret[ix] = value
        return ret

    @property
    def time(self):
        if len(self._time) != len(self):
            self._time = [task.time for task in self]
            #self._time = self.createArray('time')
        return self._time

    @property
    def ue(self):
        if len(self._ue) != len(self):
            self._ue = self.createArray('estimated_runtime_uncorrected')
        return self._ue

    @property
    def ct(self):
        if len(self._ct) != len(self):
            self._ct = self.createArray('final_cpu_time')
        return self._ct

    @property
    def fe(self):
        if len(self._fe) != len(self):
            self._fe = self.createArray('rsc_fpops_est')
        return self._fe

    @property
    def et(self):
        if len(self._et) != len(self):
            self._et = self.createArray('final_elapsed_time')
        return self._et

    @property
    def names(self):
        if len(self._names) != len(self):
            self._names = [task.name for task in self]
        return self._names

    def setColor(self, ax):
        try:
            self.color = projectColors.colors[self.label]
        except KeyError:
            logger.debug('Vops, no color found for %s', self.label)
            self.color = ax._get_lines.color_cycle.next()
            projectColors.colors[self.label] = self.color

    def plot(self, fig):
        """ Plots the job_log to the given figure instance
        """
        if len(self.time) == 0:
            return

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
        self.setColor(ax1)
        self.plot_datapoints(axes)
        self.plot_hist_day(axes)
        
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

        kwargs = dict(ls='none', marker='o', color=self.color)
        for ix, data in enumerate([self.ue, self.ct, self.et, self.fe]):
            if ix == 3:
                data = np.array(data)/1e12
            axes[ix].plot(time, data, **kwargs)

    def plot_hist_day(self, axes):
        """
        Create a single bar for each day
        """
        time, ue, ct, fe, name, et = self.time, self.ue, self.ct, self.fe, self.names, self.et

        currentDay = time[0]#plt.num2date(time[0])
        cumulative = np.zeros(4) # [ue, ct, et, fe]
        #cumulative = np.zeros(3) # [ue, ct, et]

        def myBarPlot(currentDay, cumulative, **kwargs):
            d = currentDay.replace(hour=0, minute=0, second=0, microsecond=0) # Reset to 0:00:00 this day for alignment of bars
            x = plt.date2num(d)
            # Plot bars
            kwargs['width'] = 1
            kwargs['alpha'] = 0.75
            kwargs['color'] = self.color
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

    def plot_FoM(self, fig):
        """Figure of Merits plot"""
        if len(self.time) == 0:
            return

        estimate_accuracy = self.ct/self.ue # estimated/cpu
        efficiency = self.ct/self.et        # cpu/clock
        credits_ = self.credit/self.ct      # [credit/cpu] = credits/hour
        data = (estimate_accuracy,
                efficiency,
                credits_)
        labels = ('Estimate accuracy',
                  'Efficiency',
                  'Credits per hour')
        
        N = 3
        kwargs = dict(ls='none', marker='o', 
                      color=self.color, label=self.label)
        for ix in range(N):
            ax = fig.add_subplot(N, 1, ix+1)
            ax.plot(self.time, data[ix], **kwargs)
            ax.set_ylabel(labels[ix])
            ax.set_xlabel('Date')
            dayFormat(ax)
            if ix != N-1: # last axes
                plt.setp(ax.get_xticklabels(), visible=False)            

        leg = ax.legend()
        if leg is not None:
            leg.draggable()
        

class JobLog_Months(JobLog):
    """ JobLog focus is on single events summed up to one day, 
    this class focuses on days being summed to months
    """
    def plot_datapoints(self, axes):
        JobLog.plot_hist_day(self, axes)

    def plot_hist_day(self, axes):
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
            kwargs['color'] = self.color
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


def plotAll(fig1, fig2, fig3, web_projects, BOINC_DIR):
    projects = dict()
    for p in web_projects.values():
        url = Project(url=p.url)
        projects[url.name] = p.name

    for url, filename in util.getLocalFiles(BOINC_DIR, 'job_log', '.txt'):
        try:
            p = Project(url=url)
            label = projects[p.name]
        except KeyError:
            logger.warning('Could not find url %s in %s', url, projects)
            label = url

        tasks = createFromFilename(JobLog, filename, 
                                   label=label, limitMonths=1)
        tasks.plot(fig=fig1)
        tasks.plot_FoM(fig=fig3)

        tasks = createFromFilename(JobLog_Months, filename, 
                                   label=label, limitMonths=120)
        tasks.plot(fig=fig2)

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.DEBUG)
    
    import config
    import boinccmd
    
    _, _, BOINC_DIR = config.set_globals()

    local_projects = boinccmd.get_state(command='get_project_status')

    fig1 = plt.figure()
    fig2 = plt.figure()
    fig3 = plt.figure()
    plotAll(fig1, fig2, fig3, local_projects, BOINC_DIR)

    raw_input('=== Press enter to exit ===\n')
