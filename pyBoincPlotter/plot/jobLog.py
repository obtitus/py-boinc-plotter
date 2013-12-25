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
import itertools
import time
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

def decay_average(t, y, now=0):
    """Modified from http://boinc.berkeley.edu/trac/wiki/CreditStats
function decay_average($avg, $avg_time, $now = 0) {
   $M_LN2 = 0.693147180559945309417;
   $credit_half_life = 86400 * 7;
   if ($now == 0) {
       $now = time();
   }
   $diff = $now - $avg_time;
   $weight = exp(-$diff * $M_LN2/$credit_half_life);
   $avg *= $weight;
   return $avg;
}
    """
    M_LN2 = 0.693147180559945309417
    credit_half_life = 7#86400 * 7, matplotlib deals in days
    if now == 0:
        now = datetime.datetime.now()
        now = plt.date2num(now)

    diff = now - t
    weight = np.exp(-diff*M_LN2/credit_half_life)
    # print 't, y', t, y
    # print '-diff', -diff, M_LN2, credit_half_life
    # print 'weight', weight
    return sum(y*weight)/sum(weight)

def createFromFilename(filename, limitMonths=None):
    """ Returns a JobLog instance from a given filename
    """
    try:
        with open(filename, 'r') as f:
            return createFromFilehandle(f, limitMonths=limitMonths)
    except Exception as e:
        logger.exception('Error reading job_log %s', filename)

def createFromFilehandle(f, limitMonths=None):
    """ Returns a JobLog instance from a given filehandle
    ue - estimated_runtime_uncorrected
    ct - final_cpu_time, cpu time to finish
    fe - rsc_fpops_est, estimated flops
    et - final_elapsed_time, clock time to finish
    """
    #logger.debug('createFromFilehandle(%s, %s)', f, limitMonths)
    tasks = list()
    now = datetime.datetime.now()
    for line in f:
        t = task.Task_jobLog.createFromJobLog(line)
        if limitMonths == None or util.diffMonths(t.time, now) < limitMonths:
            #logger.debug('Appending from JobLog %s', t)
            tasks.append(t)
    return tasks

def merge(tasks, web_project):
    """ Merge tasks from given project into existing list """
    # Create a dictionary for faster lookup. todo: benchmark
    names = dict()
    for ix, task in enumerate(tasks):
        names[task.name] = tasks[ix]

    for web_task in web_project.tasks():
        try:
            web_name = web_task.name
            web_name = web_name.replace('--', '') # worldcommunitygrid appends -- at the end
            names[web_name].credit = web_task.grantedCredit
        except KeyError:
            if web_task.state_str != 'in progress':
                logger.debug('Unable to find "%s", %s', 
                             web_task.name, web_task.state_str)
        except AttributeError:
            logger.debug('Not a web task %s', web_task)

class Plot(object):
    def __init__(self, tasks, limitMonths=1, minDays=15, label=''):
        """Show at least minDays, but only limitMonths months"""
        self.label = label
        self.ax = list()
        # First figure out the length:
        now = datetime.datetime.now()
        time = list()
        for t in tasks:
            if abs((now - t.time).days) < minDays or util.diffMonths(t.time, now) < limitMonths:
                time.append(t.time)

        self.time = np.array(time) #self.createArray('time', dtype=datetime.datetime)
        self.N = len(self.time)

        self.estimated_runtime_uncorrected = self.createArray(tasks, 'estimated_runtime_uncorrected')
        self.final_cpu_time = self.createArray(tasks, 'final_cpu_time')
        self.final_elapsed_time = self.createArray(tasks, 'final_elapsed_time')
        self.rsc_fpops_est = self.createArray(tasks, 'rsc_fpops_est')
        self.credit = self.createArray(tasks, 'credit')


    def createArray(self, tasks, attr, dtype=np.float):
        """ helper function for __init__ """
        ret = np.zeros(self.N, dtype=dtype)
        for ix in xrange(self.N): # Get only N tasks
            try:
                value = getattr(tasks[-ix], attr) # remember to go the other way
            except AttributeError:
                value = np.nan
            except IndexError:
                value = np.nan
            ret[-ix] = value
        return ret

    def setColor(self, ax):
        try:
            self.color = projectColors.colors[self.label]
        except KeyError:
            logger.debug('Vops, no color found for %s', self.label)
            self.color = ax._get_lines.color_cycle.next()
            projectColors.colors[self.label] = self.color

    def myPlot(self, fig1, plot_single, fig2=None, month=False, **kwargs):
        """Calls plot_cmd(ax, t, y, ylabel, **kwargs) with the correct axis and y value"""
        N = 4
        ax = list()
        for ix in range(N):
            if len(self.ax) > ix:
                ax.append(self.ax[ix]) # Already created
            else:
                sharex = None
                if ix != 0:
                    sharex = ax[0]

                sharey = None
                if ix in (1, 2):
                    sharey = ax[0]

                ax.append(fig1.add_subplot(N, 1, ix+1, 
                                           sharex=sharex, sharey=sharey))
        if fig2 != None:
            for ix in range(N):
                if len(self.ax) > ix+N:
                    ax.append(self.ax[ix+N]) # Already created
                else:
                    sharex = None
                    if ix != 0:
                        sharex = ax[N] # ugly
                    ax.append(fig2.add_subplot(N, 1, ix+1,
                                               sharex=sharex))
            
        self.setColor(ax[0])    # ugly hack.
        self.ax = ax

        try:
            plot_single(ax[0], self.estimated_runtime_uncorrected, 'Estimated time', **kwargs)
            plot_single(ax[1], self.final_cpu_time, 'Final CPU time', **kwargs)
            plot_single(ax[2], self.final_elapsed_time, 'Final clock time', **kwargs)
            plot_single(ax[3], self.rsc_fpops_est, 'flops', **kwargs)

            credit = np.where(self.credit != 0,
                              self.credit, np.nan)
            plot_single(ax[4], credit, 'Credits', **kwargs)

            # clock/estimated, value of 1 is excellent, larger than 1 means overestimated, smaller is underestimated
            accuracy = (self.final_elapsed_time-self.estimated_runtime_uncorrected)/self.estimated_runtime_uncorrected
            plot_single(ax[5], accuracy, 'Estimate accuracy', **kwargs)

            # clock/cpu, value of 1 is efficient, larger than 1 means more cpu time then clock time
            efficiency = np.where(self.final_cpu_time != 0, # avoid divison by 0
                                  (self.final_elapsed_time - self.final_cpu_time)/self.final_cpu_time, np.nan)
            plot_single(ax[6], efficiency, 'Efficiency', **kwargs)

            # [credit/cpu] = credits/hour
            credits_hours = credit/(self.final_elapsed_time/3600.)
            plot_single(ax[7], credits_hours, 'Credits per hour', **kwargs)
        except IndexError as e: # thrown if fig2 is None
            pass

    def plot_points(self, ax, y, ylabel, **kwargs):
        """Deals with a single axis for plotting data as points"""
        if len(y) == 0 or np.all(np.isnan(y)):
            return

        ax.plot(self.time, y, ls='none',
                marker='o', color=self.color, **kwargs)
        self.annoteAxis(ax, y, ylabel)

    def annoteAxis(self, ax, y, ylabel):
        y_min, y_max = ax.get_ybound()
        y_min = max([min(y), y_min])
        if y_min == 0: y_min = 1

        if ylabel.endswith('time'):
            ax.yaxis.set_major_formatter(formatter_timedelta)
        elif ylabel == 'flops':
            scale, si = util.engineeringUnit(y_max)
            ylabel = si + ylabel
            siFormatter(ax, scale)
        elif np.log10(abs(y_max/y_min)) > 3:
            ax.set_yscale('log')

        ax.set_ylabel(ylabel)

    def plot_bars_daily(self, ax, y, ylabel, **kwargs):
        self.plot_bars('day', ax, y, ylabel, **kwargs)

    def plot_bars_montly(self, ax, y, ylabel, **kwargs):
        self.plot_bars('month', ax, y, ylabel, **kwargs)

    def plot_bars(self, mode, ax, y, ylabel, **kwargs):
        """Deals with a single axis for plotting data as bars.
        Mode must be either 'day' or 'month'"""
        assert mode in ('day', 'month'), 'Vops, somethings very wrong, mode is %s' % mode

        days = list()
        width = list()
        cumulative = list()
        bottom = list()
        ix = 0
        for key, group in itertools.groupby(self.time, lambda k: getattr(k, mode)):
            c = 0               # cumulative
            for count in group: # we just need to run the length of the iterator
                c += y[ix]
                ix += 1
            now = count.replace(hour=0, minute=0, second=0, microsecond=0) # Reset to 0:00:00 this day for alignment of bars
            if mode == 'month':
                # replace day as well
                now = now.replace(day=1)

            days.append(now)
            cumulative.append(c)
            w = 1
            if mode == 'month':
                _, w = calendar.monthrange(now.year,
                                               now.month)
            width.append(w)

            try:
                b = ax.__bottom[now]
                bottom.append(b)
            except AttributeError:  # first time calling (no ax.__bottom)
                bottom.append(0)
                ax.__bottom = dict()
            except KeyError:    # day which is not present in any other dataset
                bottom.append(0)
            ax.__bottom[now] = bottom[-1] + c
                

        logger.debug("Bottom: %s, %s", self.label, bottom)

        ax.bar(days, cumulative, color=self.color, 
               width=width, alpha=0.75, bottom=bottom, 
               **kwargs)
        self.annoteAxis(ax, [0], ylabel)

    def addAverageLine(self):
        for ax in self.ax:
            try:
                N = len(ax.__bottom)
            except AttributeError:
                continue

            time, value = np.zeros(N), np.zeros(N)
            ix = 0
            for t, y in ax.__bottom.items(): # we could sort, but we don't need to
                time[ix], value[ix] = plt.date2num(t), y
                ix += 1

            avg = decay_average(time, value)
            logger.debug('AVG %s', avg)
            ax.axhline(avg, color='k', ls='--', alpha=0.5)
            # annotate:
            form = ax.yaxis.get_major_formatter()
            s = form(avg)
            x_min, x_max = ax.get_xlim()
            xy = (x_max, avg)
            ax.annotate(s, xy, fontsize='x-small')
            
#     @property
#     def time(self):
#         if len(self._time) != len(self):
#             self._time = [task.time for task in self]
#             #self._time = self.createArray('time')
#         return self._time

#     @property
#     def ue(self):
#         if len(self._ue) != len(self):
#             self._ue = self.createArray('estimated_runtime_uncorrected')
#         return self._ue

#     @property
#     def ct(self):
#         if len(self._ct) != len(self):
#             self._ct = self.createArray('final_cpu_time')
#         return self._ct

#     @property
#     def fe(self):
#         if len(self._fe) != len(self):
#             self._fe = self.createArray('rsc_fpops_est')
#         return self._fe

#     @property
#     def et(self):
#         if len(self._et) != len(self):
#             self._et = self.createArray('final_elapsed_time')
#         return self._et

#     @property
#     def credit(self):
#         if len(self._credit) != len(self):
#             self._credit = self.createArray('credit')
#         return self._credit

#     @property
#     def names(self):
#         if len(self._names) != len(self):
#             self._names = [task.name for task in self]
#         return self._names

#     def setColor(self, ax):
#         try:
#             self.color = projectColors.colors[self.label]
#         except KeyError:
#             logger.debug('Vops, no color found for %s', self.label)
#             self.color = ax._get_lines.color_cycle.next()
#             projectColors.colors[self.label] = self.color

#     def plot(self, fig):
#         """ Plots the job_log to the given figure instance
#         """
#         if len(self.time) == 0:
#             return

#         N = 4                               # Number of subplots
#         self.axes = list()
#         ax1 = fig.add_subplot(N, 1, 1)
#         for ix in range(N):
#             if ix != 3:
#                 ax = fig.add_subplot(N, 1, ix+1)#, sharey=ax1)
#             else:
#                 ax = fig.add_subplot(N, 1, ix+1)
#             barPlotter = BarPlotter(ax)
#             self.axes.append(barPlotter)

#         # Plot datapoints and bars, make sure the same colors are used.
#         self.setColor(ax1)
#         self.plot_datapoints()
#         self.plot_hist_day()
        
#         self.formatAxis()

#     def formatXAxis(self, ax):
#         dayFormat(ax)

#     def formatAxis(self):
#         for ax in self.axes:
#             self.formatXAxis(ax)

#         leg = self.axes[3].legend()
#         if leg is not None:
#             leg.draggable()

#         ylabels = ['Estimated time', 'Final CPU time', 'Final clock time', 'flops']
#         for ix, ax in enumerate(self.axes):
#             ax.set_xlabel('Date')
#             if ix == len(self.axes)-1: # last axes
#                 y_min, y_max = ax.get_ybound()
#                 scale, si = util.engineeringUnit(y_max)
#                 ylabels[ix] = si + ylabels[ix]
#                 siFormatter(ax, scale)
#             else:
#                 ax.yaxis.set_major_formatter(formatter_timedelta)
#                 plt.setp(ax.get_xticklabels(), visible=False)

#             ax.set_ylabel(ylabels[ix])

#     def plot_datapoints(self):
#         """
#         Let each datapoint be a single dot
#         """
#         time = self.time

#         kwargs = dict(ls='none', marker='o', color=self.color)
#         for ix, data in enumerate([self.ue, self.ct, self.et, self.fe]):
#             self.axes[ix].plot(time, data, **kwargs)

#     def plot_hist_day(self):
#         """
#         Create a single bar for each day
#         """
#         time, ue, ct, fe, name, et = self.time, self.ue, self.ct, self.fe, self.names, self.et

#         currentDay = time[0]#plt.num2date(time[0])
#         cumulative = np.zeros(4) # [ue, ct, et, fe]
#         #cumulative = np.zeros(3) # [ue, ct, et]

#         def myBarPlot(currentDay, cumulative, **kwargs):
#             d = currentDay.replace(hour=0, minute=0, second=0, microsecond=0) # Reset to 0:00:00 this day for alignment of bars
#             x = plt.date2num(d)
#             # Plot bars
#             kwargs['width'] = 1
#             kwargs['alpha'] = 0.75
#             kwargs['color'] = self.color
#             self.axes[0].bar(x, cumulative[0], **kwargs)
#             self.axes[1].bar(x, cumulative[1], **kwargs)
#             self.axes[2].bar(x, cumulative[2], **kwargs)
#             self.axes[3].bar(x, cumulative[3], **kwargs)

#         for ix in range(len(time)):
#             # If new day, plot and null out cumulative
#             if currentDay.day != time[ix].day:
#                 myBarPlot(currentDay, cumulative)
#                 # Prepare for next loop
#                 currentDay = time[ix]
#                 cumulative = np.zeros(len(cumulative))

#             # Add events associated with time[ix]
#             cumulative[0] += ue[ix]
#             cumulative[1] += ct[ix]
#             cumulative[2] += et[ix]
#             cumulative[3] += fe[ix]

#         # plot last day
#         myBarPlot(time[-1], cumulative, label=self.label)

#     def plot_FoM(self, fig):
#         """Figure of Merits plot"""
#         if len(self.time) == 0:
#             return

#         # clock/estimated, value of 1 is excellent, larger than 1 means overestimated
#         estimate_accuracy = self.et/self.ue
#         # clock/cpu, value of 1 is efficient, larger than 1 means more cpu time then clock time
#         ct = self.ct
#         ct[np.where(ct == 0)] = np.nan # avoids division by zero
#         efficiency = self.et/ct
#         # [credit/cpu] = credits/hour
#         credits_ = np.where(self.credit != 0,
#                             self.credit/(self.et/3600.), np.nan)

#         data = (estimate_accuracy,
#                 efficiency,
#                 credits_)
#         labels = ('Estimate accuracy',
#                   'Efficiency',
#                   'Credits per hour')
        
#         N = 3
#         kwargs = dict(ls='none', marker='o', 
#                       color=self.color, label=self.label)

#         ax = fig.add_subplot(N, 1, 1)
#         for ix in range(N):
#             if ix != 0:
#                 ax = fig.add_subplot(N, 1, ix+1, sharex=ax)

#             ax.plot(self.time, data[ix], **kwargs)

#             ymin, ymax = ax.get_ylim()
#             ymin = max([min(data[ix]), ymin])
#             if ymin == 0: ymin = 1

#             if np.log10(abs(ymax/ymin)) > 3:
#                 logger.debug('logarithmic axis for %s', labels[ix])
#                 ax.set_yscale('log')

#             ax.set_ylabel(labels[ix])
#             if ix != N-1: # last axes
#                 plt.setp(ax.get_xticklabels(), visible=False)            

#         ax.set_xlabel('Date')
#         dayFormat(ax)

#         leg = ax.legend()
#         if leg is not None:
#             leg.draggable()
#             leg.draw_frame(False)

#     def appendAverage(self):
#         for ax in self.axes:
#             N = len(ax.bottom)
#             time, value = np.zeros(N), np.zeros(N)
#             ix = 0
#             for t, y in ax.bottom.items(): # we could sort, but we don't need to
#                 time[ix], value[ix] = t, y
#                 ix += 1
            
#             avg = decay_average(time, value)
#             logger.debug('AVG %s', avg)
#             ax.axhline(avg, color='k', ls='--')
#             #ax.annotate("{}".format(avg), (max(time)+1, avg))

# class JobLog_Months(JobLog):
#     """ JobLog focus is on single events summed up to one day, 
#     this class focuses on days being summed to months
#     """
#     def plot_datapoints(self):
#         JobLog.plot_hist_day(self)

#     def plot_hist_day(self):
#         """ Replaces hist_day with hist_month
#         """
#         time, ue, ct, fe, name, et = self.time, self.ue, self.ct, self.fe, self.names, self.et

#         if len(time) == 0: return ;         # make sure we actually have data to work with

#         currentDay = time[0]
#         cumulative = np.zeros(4) # [ue, ct, et, fe]

#         def myBarPlot(currentDay, cumulative, **kwargs):
#             d = currentDay.replace(day=1, hour=0, minute=0, 
#                                    second=1, microsecond=0) # Reset to 0:00:00 this month for alignment of bars
#             x = plt.date2num(d)
#             # Plot bars
#             _, daysInMonth = calendar.monthrange(currentDay.year,
#                                                  currentDay.month)
#             kwargs['width'] = daysInMonth
#             kwargs['alpha'] = 0.5
#             kwargs['color'] = self.color
#             self.axes[0].bar(x, cumulative[0], **kwargs)
#             self.axes[1].bar(x, cumulative[1], **kwargs)
#             self.axes[2].bar(x, cumulative[2], **kwargs)
#             self.axes[3].bar(x, cumulative[3], **kwargs)

#         for ix in range(len(time)):
#             # If new month, plot and null out cumulative
#             if currentDay.month != time[ix].month:
#                 myBarPlot(currentDay, cumulative)
#                 # Prepare for next loop
#                 currentDay = time[ix]
#                 cumulative = np.zeros(len(cumulative))

#             # Add events associated with time[ix]
#             cumulative[0] += ue[ix]
#             cumulative[1] += ct[ix]
#             cumulative[2] += et[ix]
#             cumulative[3] += fe[ix]

#         # plot last month
#         myBarPlot(time[-1], cumulative)
        

#     def formatXAxis(self, ax):
#         dayFormat(ax, month=True)

# class BarPlotter(object):
#     # Bar plotter that remembers bottom
#     # and automatically plots bars stacked instead of on top of each other
#     # Assumes that bar is called with only a single bar at a time
#     def __init__(self, ax):
#         self.ax = ax
#         if not(hasattr(self.ax, 'bottom')):
#             self.ax.bottom = dict()     # key is x coordinate and value is height

#     def clear(self):
#         print 'clearing', self.ax.bottom
#         self.ax.bottom = dict()
        
#     def __getattr__(self, name):
#         """ Redirect to axes
#         """
#         return self.ax.__getattribute__(name)

#     def bar(self, x, *args, **kwargs):
#         # Find previous (if any)
#         try:
#             b = self.ax.bottom[x]
#         except KeyError:
#             b = 0
#         kwargs['bottom'] = b
#         # Plot
#         rect = self.ax.bar(x, *args, **kwargs)[0]

#         # Remember
#         x, y = rect.get_xy()
#         self.ax.bottom[x] = y + rect.get_height()
#         return b

#     # def plot(self, *args, **kwargs):
#     #     self.ax.plot(*args, **kwargs)


def plotAll(fig1, fig2, fig3, web_projects, BOINC_DIR):
    projects = dict()
    for p in web_projects.values():
        url = Project(url=p.url)
        projects[url.name] = p

    for url, filename in util.getLocalFiles(BOINC_DIR, 'job_log', '.txt'):
        try:
            p = Project(url=url)
            project = projects[p.name]
            label = project.name
        except KeyError:
            logger.warning('Could not find url %s in %s', url, projects)
            project = None
            label = url

        tasks = createFromFilename(filename, limitMonths=120)
        if project is not None:
            merge(tasks, project)
        # for t in  tasks:
        #     print t, getattr(t, 'credit', None)
        p_daily = Plot(tasks, limitMonths=1, label=label)
        p_daily.myPlot(fig1, p_daily.plot_points, fig2=fig2, label=label)
        p_daily.myPlot(fig1, p_daily.plot_bars_daily)

        p = Plot(tasks, limitMonths=120, label=label)
        #p.myPlot(fig3, p.plot_points, fig2=None)
        #p.myPlot(fig3, p.plot_bars_daily, month=True)
        p.myPlot(fig3, p.plot_bars_montly, label=label, month=True)

    p_daily.addAverageLine()
    #p.addAverageLine()

    for fig in [fig1, fig2, fig3]:
        if fig != None and len(fig.axes) != 0:
            dayFormat(fig.axes[-1])#, month=month)
            addLegend(fig.axes[-1])
            for axis in fig.axes[:-1]:    # hide xlabels for all but last axis
                plt.setp(axis.get_xticklabels(), visible=False)


if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    import boinccmd
    import browser
    import project
    
    CONFIG, CACHE_DIR, BOINC_DIR = config.set_globals()
    browser_cache = browser.Browser_file(CACHE_DIR)

    local_projects = boinccmd.get_state(command='get_project_status') # Need for names
    web_projects = browser.getProjectsDict(CONFIG, browser_cache)
    project.merge(local_projects,
                  web_projects)

    fig1 = plt.figure()
    fig2 = plt.figure()
    fig3 = plt.figure()
    plotAll(fig1, fig2, fig3, web_projects, BOINC_DIR)

    raw_input('=== Press enter to exit ===\n')
