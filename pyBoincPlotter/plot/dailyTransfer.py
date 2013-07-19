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
import xml.etree.ElementTree
from collections import defaultdict
import logging
logger = logging.getLogger('boinc.plot.dailyTransfer')
# This project
from importMatplotlib import *

def parse(page, limitDays):
    """
    Returns a dictionary which should contain a list of 'when', 'up' and 'down'
    """
    tree = xml.etree.ElementTree.parse(page)
    data = defaultdict(list)
    now = datetime.datetime.now()
    for d in tree.iter('dx'):
        for child in d:
            if child.tag == 'when':
                item = float(child.text)
                item = datetime.datetime.fromtimestamp(item*60*60*24)
                if limitDays == None or (now - item).days < limitDays:
                    data[child.tag].append(plt.date2num(item))
                else:
                    break
            else:
                item = float(child.text)
                data[child.tag].append(float(item))

    for key in data:
        data[key] = np.array(data[key])

    return data

def plot(fig, data):
    day = data['when']
    up, down = data['up']/1e6, data['down']/1e6

    fig.suptitle('Total upload/download = {0:.3g} MB/{1:.3g} MB'.format(sum(up), sum(down)))
    ax = fig.add_subplot(111)
    kwargs = dict(align='center')
    for ix in range(len(day)):
        ax.bar(day[ix], up[ix], color='b', **kwargs)
        ax.bar(day[ix], -down[ix], color='r', **kwargs)

    ax.set_xlabel('Date')
    ax.set_ylabel('upload/-download MB')
    dayFormat(ax)

def getFilename(BOINC_DIR):
    return os.path.join(BOINC_DIR, 'daily_xfer_history.xml')

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    
    _, _, BOINC_DIR = config.set_globals()
    fig1 = plt.figure()
    
    data = parse(getFilename(BOINC_DIR), limitDays=15)
    plot(fig1, data)

    raw_input('=== Press enter to exit ===\n')