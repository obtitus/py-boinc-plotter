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
import os
import datetime
import re
import xml.etree.ElementTree
from collections import defaultdict
import calendar

import logging
logger = logging.getLogger('boinc.statistics_plot')

from loggerSetup import loggerSetup
from importMatplotlib import *
import config
import async

import stacked_graph

limitDaysToPlot = datetime.timedelta(days=15)
def dayFormat(ax):
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=1))
#     N = len(ax.get_xticks())
#     if N > 20:
#         ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=N//15))    
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
    kwargs = dict(marker='*', ls='-')
    ax1.plot(data['day'], data['user_total_credit'], label='{0} user total'.format(name), **kwargs)
    ax1.plot(data['day'], data['host_total_credit'], label='{0} host total'.format(name), **kwargs)
    ax1.legend(loc='best').draggable()
    ax1.set_ylabel('Total boinc credit')

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.plot(data['day'], data['user_expavg_credit'], label='{0} user average'.format(name), **kwargs)
    ax2.plot(data['day'], data['host_expavg_credit'], label='{0} host average'.format(name), **kwargs)
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
    for line in page:
        s = line.split()
        assert len(s) == 11, 'Line in job log not recognized {0} "{1}" -> "{2}"'.format(len(s), line, s)
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
    l4 = ax4.plot(time, np.array(fe)/1e9, label=projectName, **kwargs)
    ax4.set_ylabel('Gflops')

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
        b4.bar(x, cumulative[3]/1e9, width=1, alpha=0.5, color=color[3])

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

def plotStream(inputStream, labels, color):
    now = datetime.datetime.now()
    cal = calendar.Calendar()
    days = list(cal.itermonthdates(year=now.year, month=now.month))
    N = len(days)
#     N = 0
#     for data in inputStream:
#         N = max(N, len(data['time']))
        
    stream = list()
    for data in inputStream:
        #time, ue, ct, fe, name, et = data['time'], data['ue'], data['ct'], data['fe'], data['name'], data['et']
        
        this_dset = np.zeros(N)
        for ix in range(len(data['time'])):
            date = plt.num2date(data['time'][ix])
            #date = datetime.datetime(year=date.year, month=date.month, day=date.day)
            #jx = days.index(date)
            for jx in range(N):
                if date.year == days[jx].year and date.month == days[jx].month and date.day == days[jx].day:
                    break
            else:
                continue
            this_dset[jx] += data['ue'][ix]

        stream.append(this_dset)

    stacked_graph.stacked_graph(days, stream, labels, baseline_fn = stacked_graph.zero, color_seq=color)
    plt.gcf().autofmt_xdate()
    plt.gca().yaxis.set_major_formatter(formatter_timedelta)
#    for day in days:
#        plt.num2date(time[ix])
        
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

    try:
        fig = plt.figure('Stream plot', figsize=(10, 8))
        fig.clf()
        plotStream(stream, labels=labels, color=color)
    except Exception as e:
        logger.error('Stream plot error %s', e)
        #fig.close()

    fig = plt.figure('daily transfer', figsize=(10, 8))
    fig.clf()
    if daily_transfer.ret != None:
        plotDailyTransfer(fig, daily_transfer.ret)

if __name__ == '__main__':
    loggerSetup(logging.INFO)

    ### Make global variables ###
    config.main()

    main()
    raw_input('=== Press enter to exit ===\n')