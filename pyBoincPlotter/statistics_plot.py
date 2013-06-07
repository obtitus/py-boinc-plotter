#!/usr/bin/env python
# This file is part of the py-boinc-plotter, which provides parsing and plotting of boinc statistics and badge information.
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
# 
# END LICENCE
"""
Plots the local status files that boinc generates:
job_log_<project>.txt
statistics_<project>.xml
daily_xfer_history.xml
todo?: time_stats_log
Files are skipped if not found, or if they can't be opened.
"""
from __future__ import division
import os
import datetime
import re
import xml.etree.ElementTree
from collections import defaultdict, namedtuple
import calendar

import logging
logger = logging.getLogger('boinc.statistics_plot')

from loggerSetup import loggerSetup
from importMatplotlib import *
import config
import async


limitDaysToPlot = datetime.timedelta(days=15)
def dayFormat(ax):
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=1))
    try:
        N = len(ax.get_xticks())
    except RuntimeError as e:
        logger.warning('day format error %s', e)
        N = 10000
    if N > 20:
        ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=N//15))
            
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
    for label in ax.get_xticklabels():
        label.set_rotation(17)
        label.set_ha('right')


def getFile(filename, directory=None):
    if directory == None:
        directory = config.BOINC_DIR
    try:
        f = os.path.join(directory, filename)
        page = open(f, 'r')
        return page
    except IOError as e:
        logger.warning('Unable to open file {0}, error {1}'.format(f, e))
        return None
    
def getPages(boincDir=None, name='', extension='.xml'):
    if boincDir == None:
        boincDir = config.BOINC_DIR
    if not(os.path.exists(boincDir)):
        logger.error('Could not find boinc dir "%s"', boincDir)
        return ;

    reg_exp = '{0}_(\S*){1}'.format(name, extension)
    logger.debug(reg_exp)
    reg_exp = re.compile(reg_exp)    
    for f in os.listdir(boincDir):
        reg = re.match(reg_exp, f)
        if reg:
            project = reg.group(1)
            page = getFile(filename=f, directory=boincDir)
            if page != None:
                yield project, page

def parseStatistics(page):
    tree = xml.etree.ElementTree.parse(page)

    now = datetime.datetime.now()
    data = defaultdict(list)
    for d in tree.iter('daily_statistics'):
        for child in d:
            if child.tag == 'day':
                item = float(child.text)
                item = datetime.datetime.fromtimestamp(item)
                if limitDaysToPlot == None or now - item < limitDaysToPlot:
                    data[child.tag].append(plt.date2num(item))
                else:
                    break
            else:
                item = float(child.text)
                data[child.tag].append(float(item))
    return data

def plotStatistics(fig, data, name):
    ax1 = fig.add_subplot(211)
    kwargs = dict(ls='-')
    l = ax1.plot(data['day'], data['user_total_credit'], label='{0}'.format(name), **kwargs)

    kwargsHost = dict(marker='*', ls='-', color=l[0].get_color())
    ax1.plot(data['day'], data['host_total_credit'], **kwargsHost)
    ax1.legend(loc='best').draggable()
    ax1.set_ylabel('Total boinc credit')

    ax2 = fig.add_subplot(212, sharex=ax1)
    l = ax2.plot(data['day'], data['user_expavg_credit'], label='{0}'.format(name), **kwargs)

    kwargsHost['color'] = l[0].get_color()
    ax2.plot(data['day'], data['host_expavg_credit'], **kwargsHost)
    ax2.legend(loc='best').draggable()

    ax2.set_xlabel('Date')
    ax2.set_ylabel('Average boinc credit')

    for ax in [ax1, ax2]:
        dayFormat(ax)
            
def parseJobLog(page):
    time = list()
    ue = list()                         # estimated_runtime_uncorrected, 'Col 2: 344.039352 I think is time in seconds but I don't yet fully understand it.'
    ct = list()                         # final_cpu_time, 'Col 3: 80.234380 Is CPU time required to manage the CUDA card.' or 'The blue field is the number of seconds the CPU worked on the task'
    fe = list()                         # wup->rsc_fpops_est, 'Col 4: 23780000000000.000000 is flops, I think.'
    name = list()                       # name, 'wu name'
    et = list()                         # final_elapsed_time, 'Col 6: 501.640625 is the clock time in seconds that it took to complete the WU.' or 'The green field is the elapsed time for the task.'
    now = datetime.datetime.now()
    for ix, line in enumerate(page):
        s = line.split()
        #assert len(s) == 11, 
        if len(s) != 11:
            logger.warning('Line {} in job log not recognized, split length {} "{}" -> "{}"'.format(ix, len(s), line, s))
            continue
        t = int(s[0])
        t = datetime.datetime.fromtimestamp(t)
        if limitDaysToPlot == None or now - t < limitDaysToPlot:
            time.append(plt.date2num(t))
            ue.append(float(s[2]))
            ct.append(float(s[4]))
            fe.append(float(s[6]))
            name.append(s[8])
            et.append(float(s[10]))

    data = dict(ue=ue, ct=ct, fe=fe, name=name, et=et, time=time)
    return data

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
        
def plotJobLog(fig, data, projectName, prevBars=None):
    N = 4                               # Number of subplots
    ix = 1                              # current subplot
    kwargs = dict(ls='none', marker='o')
    time, ue, ct, fe, name, et = data['time'], data['ue'], data['ct'], data['fe'], data['name'], data['et']
    
    ax1 = fig.add_subplot(N, 1, ix); ix += 1
    l1 = ax1.plot(time, ue, label=projectName, **kwargs)
    ax1.set_ylabel('Estimated time')    # uncorrected

    ax2 = fig.add_subplot(N, 1, ix, sharex=ax1, sharey=ax1); ix += 1
    l2 = ax2.plot(time, ct, label=projectName, **kwargs)
    ax2.set_ylabel('Final CPU time')

    ax3 = fig.add_subplot(N, 1, ix, sharex=ax1, sharey=ax1); ix += 1    
    l3 = ax3.plot(time, et, label=projectName, **kwargs)    
    ax3.set_ylabel('Final clock time')

    ax4 = fig.add_subplot(N, 1, ix, sharex=ax1); ix += 1
    l4 = ax4.plot(time, np.array(fe)/1e12, label=projectName, **kwargs)
    ax4.set_ylabel('Tflops')

    color = [l1[0].get_color(), l2[0].get_color(), l3[0].get_color(), l4[0].get_color()]

    ax4.legend().draggable()
    
    for ax in fig.axes:
        ax.set_xlabel('Date')
    for ax in [ax1, ax2, ax3]:
        plt.setp(ax.get_xticklabels(), visible=False)
        ax1.yaxis.set_major_formatter(formatter_timedelta)

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

        
def parseDailyTransfer(page):
    # Not sure about the unit
    tree = xml.etree.ElementTree.parse(page)
    data = defaultdict(list)
    now = datetime.datetime.now()
    for d in tree.iter('dx'):
        for child in d:
            if child.tag == 'when':
                item = float(child.text)
                item = datetime.datetime.fromtimestamp(item*60*60*24)
                if limitDaysToPlot == None or now - item < limitDaysToPlot:
                    data[child.tag].append(plt.date2num(item))
                else:
                    break
            else:
                item = float(child.text)
                data[child.tag].append(float(item))
    return data

def plotDailyTransfer(fig, data):
    day, up, down = data['when'], data['up'], data['down']

    fig.suptitle('Total upload/download = {0}/{1}'.format(sum(up), sum(down)))
    ax = fig.add_subplot(111)
    kwargs = dict(align='center')
    for ix in range(len(day)):
        ax.bar(day[ix], up[ix], color='b', **kwargs)
        ax.bar(day[ix], -down[ix], color='r', **kwargs)

    ax.set_xlabel('Date')
    ax.set_ylabel('upload/download')
    dayFormat(ax)

def parseTimeStats(page):
    """
    Parses the time_stats_log, returns time and description iterators
    """
    for line in page:
        s = line.split()
        if len(s) == 3: continue # version and platform are longer
        elif s[0] == '': continue
        elif len(s) != 2:
            logger.warning('time_stats_log line not recognized "{}"'.format(line))
            continue

        t = float(s[0])
        t = datetime.datetime.fromtimestamp(t)
        desc = s[1]

        yield plt.date2num(t), desc

def plotTimeStats(fig, data, limitDays=None):
    now = plt.date2num(datetime.datetime.now())
    
    gs = gridspec.GridSpec(3, 3)
    
    class PrevState(object): # namedtuple('PreviousState', ['t', 'desc'])
        states = dict(on='green', off='red', start='green', stop='red', not_connected='red', unknown='blue')
        def __init__(self, t, desc):
            self.t = t
            self.desc = desc
            self.cumsum = defaultdict(int) # Keep a sum over all plotted
        
        def getColor(self, desc=None):
            if desc == None: desc = self.desc
            try:
                return self.states[desc]
            except KeyError:
                logger.warning('plotTimeStats unknown state "{}"'.format(desc))
                return 'k'

        def barh(self, ax, t):
            if self.t != None and (limitDays == None or now - t < limitDays.days):
                color = self.getColor()
                ax.barh(bottom=0, width=(t - self.t), left=self.t, height=1, color=color, linewidth=0)

                self.cumsum[self.desc] += (t - self.t) # todo substract outside wanted range

        def pie(self, ax):
            # use the cumsum to plot a pie chart
            x = list()
            colors = list()
            labels = list()
            for key in self.cumsum:
                x.append(self.cumsum[key])
                colors.append(self.getColor(key))
                labels.append(key.replace('_', ' ').capitalize())
                
            ax.pie(x, labels=labels, colors=colors, autopct='%.1f %%')
            
        def update(self, t, desc):
            self.t = t
            self.desc = desc

    N = 3
    power = PrevState(None, None)
    net = PrevState(None, None)
    proc = PrevState(None, None)
    ax0 = fig.add_subplot(gs[0, :-1])
    ax1 = fig.add_subplot(gs[1, :-1])
    ax2 = fig.add_subplot(gs[2, :-1])
    axes = [ax0, ax1, ax2]
    for t, desc in data:
        if desc.startswith('power'):
            newState = desc[len('power_'):]
            power.barh(ax0, t)
            power.update(t, newState)
        elif desc.startswith('net'):
            newState = desc[len('net_'):]
            net.barh(ax1, t)
            net.update(t, newState)
        elif desc.startswith('proc'):
            newState = desc[len('proc_'):]
            proc.barh(ax2, t)
            proc.update(t, newState)
        else:
            logger.warning('plotTimeStats, did not recognize "{}" as description'.format(desc))

    # Draw current state to now
    for ix, item in enumerate([power, net, proc]):
        item.barh(axes[ix], now)
        ax2 = fig.add_subplot(gs[ix, -1])
        item.pie(ax2)

    # y labels
    ticks = np.arange(N)
    labels = ['Power', 'Network', 'Processor']
    for ix, ax in enumerate(axes):
        ax.set_ylabel(labels[ix])
        if limitDays != None:
            ax.set_xlim(xmin=now-limitDays.days)
        dayFormat(ax)
        plt.setp(ax.get_yticklabels(), visible=False)
    for ax in [ax0, ax1]:
        plt.setp(ax.get_xticklabels(), visible=False)
def shortenProjectName(name):
    name = name.replace('www.', '')
    name = name.replace('.org', '')        
    return name

def main():
    def getAndParse(parser, name, extension):
        for name, page in getPages(name=name, extension=extension):
            data = parser(page)
            yield data, name

    statistics = async.AsyncGen(getAndParse, parseStatistics, name='statistics', extension='.xml')
    job_log = async.AsyncGen(getAndParse, parseJobLog, name='job_log', extension='.txt')

    def getAndParseFile(name):
        name = shortenProjectName(name)
        page = getFile(name)
        if page != None:
            return parseDailyTransfer(page)
    daily_transfer = async.Async(getAndParseFile, 'daily_xfer_history.xml')

    fig = plt.figure('boinc statistics', figsize=(10, 8))
    fig.clf()
    for data, name in statistics.ret:
        name = shortenProjectName(name)
        plotStatistics(fig, data, name)

    fig = plt.figure('job log', figsize=(10, 8))
    fig.clf()
    stream = list()
    color = list()
    labels = list()
    for data, name in job_log.ret:
        name = shortenProjectName(name) # Make the legend a bit shorter
        labels.append(name)
        color.append(plotJobLog(fig, data, name))
        stream.append(data)

    fig = plt.figure('daily transfer', figsize=(10, 8))
    fig.clf()
    if daily_transfer.ret != None:
        plotDailyTransfer(fig, daily_transfer.ret)

    fig = plt.figure('Time Stats', figsize=(10, 10))
    fig.clf()
    try:
        f = open(os.path.join(config.BOINC_DIR, 'time_stats_log'))
        data = parseTimeStats(f)
        plotTimeStats(fig, data, limitDaysToPlot)
    except Exception as e:
        logger.exception('time_stats failed with %s', e)
        try: f.close()
        except: pass
        
if __name__ == '__main__':
    loggerSetup(logging.INFO)

    ### Make global variables ###
    config.main()

    main()
    raw_input('=== Press enter to exit ===\n')
