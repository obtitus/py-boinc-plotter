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
"""
Plots the daily_xfer_history.xml file
"""
# Standard python
import os
import datetime
import calendar
import xml.etree.ElementTree
from collections import defaultdict
import logging
logger = logging.getLogger('boinc.plot.dailyTransfer')
# This project
from importMatplotlib import *
try:
    from .. import util
except ValueError:
    import util

def parse(page, limitMonths):
    """
    Returns a dictionary which should contain a list of 'when', 'up' and 'down'
    """
    tree = xml.etree.ElementTree.parse(page)
    data = defaultdict(list)
    now = datetime.datetime.utcnow()
    for d in tree.iter('dx'):
        for child in d:
            if child.tag == 'when':
                item = float(child.text)
                item = datetime.datetime.fromtimestamp(item*60*60*24)
                if limitMonths == None or util.diffMonths(item, now) < limitMonths:
                    data[child.tag].append(item)
                else:
                    break
            else:
                item = float(child.text)
                data[child.tag].append(float(item))

    for key in data:
        data[key] = np.array(data[key])

    return data

def setTitle(fig, up, down):
    s_up, s_down = sum(up), sum(down)
    fig.suptitle('Total upload/download = {}B/{}B'.format(util.fmtSi(s_up),
                                                          util.fmtSi(s_down)))
    
def plot(fig, data):
    day = data['when']
    up, down = data['up'], data['down']
    
    setTitle(fig, up, down)

    ax = fig.add_subplot(111)
    kwargs = dict(align='center', width=1)
    for ix in range(len(day)):
        ax.bar(plt.date2num(day[ix]), up[ix], color='b', **kwargs)
        ax.bar(plt.date2num(day[ix]), -down[ix], color='r', **kwargs)

    y_min, y_max = ax.get_ybound()
    y_max = max(abs(y_min), abs(y_max))
    scale, si = util.engineeringUnit(y_max)
    siFormatter(ax, scale)

    ax.set_xlabel('Date')
    ax.set_ylabel('upload/-download {}B'.format(si))
    dayFormat(ax)

def plotMonths(fig, data):
    day = data['when']
    day.sort()
    up, down = data['up'], data['down']

    setTitle(fig, up, down)
    ax = fig.add_subplot(111)

    kwargs = dict(alpha=0.5)
    for day, data in cumulativeMonth(day, (up, down)):
        day = day.replace(day=1, hour=0, minute=0, 
                          second=0, microsecond=0)
        _, daysInMonth = calendar.monthrange(day.year, day.month)

        kwargs['width'] = daysInMonth
        ax.bar(plt.date2num(day), data[0], color='b', **kwargs)
        ax.bar(plt.date2num(day), -data[1], color='r', **kwargs)

    y_min, y_max = ax.get_ybound()
    y_max = max(abs(y_min), abs(y_max))
    scale, si = util.engineeringUnit(y_max)
    siFormatter(ax, scale)

    ax.set_xlabel('Date')
    ax.set_ylabel('upload/-download {}B'.format(si))
    dayFormat(ax, month=True)

def getFilename(BOINC_DIR):
    return os.path.join(BOINC_DIR, 'daily_xfer_history.xml')

def plotAll(fig1, fig2, BOINC_DIR):
    filename = getFilename(BOINC_DIR)

    data = parse(filename, limitMonths=1)
    plot(fig1, data)

    data = parse(filename, limitMonths=12)
    plot(fig2, data)
    plotMonths(fig2, data)
    
if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    
    _, _, BOINC_DIR = config.set_globals()
    fig1 = plt.figure()
    fig2 = plt.figure()
    plotAll(fig1, fig2, BOINC_DIR)

    raw_input('=== Press enter to exit ===\n')
