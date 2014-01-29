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
import os
import collections
import logging
logger = logging.getLogger('boinc.plot.timeStats')
# This project
from importMatplotlib import *

def parse(page):
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

        yield t, desc

def plot(fig, data, limitDays=None):
    now = datetime.datetime.utcnow()
    
    gs = gridspec.GridSpec(3, 3)
    
    N = 3
    power = PrevState(None, None, limitDays=limitDays)
    net = PrevState(None, None, limitDays=limitDays)
    proc = PrevState(None, None, limitDays=limitDays)
    ax0 = fig.add_subplot(gs[0, :-1])
    ax1 = fig.add_subplot(gs[1, :-1], sharex=ax0)
    ax2 = fig.add_subplot(gs[2, :-1], sharex=ax0)
    axes = [ax0, ax1, ax2]
    for t, desc in data:
        if desc.startswith('power'):
            newState = desc[len('power_'):]
            power.barh(t, newState)
        elif desc.startswith('net'):
            newState = desc[len('net_'):]
            net.barh(t, newState)
        elif desc.startswith('proc'):
            newState = desc[len('proc_'):]
            proc.barh(t, newState)
        else:
            logger.warning('plotTimeStats, did not recognize "{}" as description'.format(desc))

    # Draw current state to now
    for ix, item in enumerate([power, net, proc]):
        item.barh(now, '')
        item.barh_draw(axes[ix])
        #item.runningPie(axes[ix])
        ax2 = fig.add_subplot(gs[ix, -1])
        item.pie(ax2)

    ticks = np.arange(N)
    labels = ['Power', 'Network', 'Processor']
    for ix, ax in enumerate(axes):
        ax.set_ylabel(labels[ix])
        plt.setp(ax.get_yticklabels(), visible=False)
        if limitDays != None:
            ax.set_xlim(xmin=plt.date2num(now)-limitDays)
        dayFormat(ax)

    for ax in [ax0, ax1]:
        plt.setp(ax.get_xticklabels(), visible=False)

class PrevState(object): # namedtuple('PreviousState', ['t', 'desc'])
    states = dict(on='green', off='red', start='green', 
                  stop='red', not_connected='red', unknown='blue')
    def __init__(self, t, desc, limitDays):
        self.t = t
        self.desc = desc
        self.cumsum = collections.defaultdict(int) # Keep a sum over all plotted
        self.now = datetime.datetime.utcnow()
        self.limitDays = limitDays

        self.data_barh = collections.defaultdict(list)

    def getColor(self, desc=None):
        if desc == None: desc = self.desc
        try:
            return self.states[desc]
        except KeyError:
            logger.warning('plotTimeStats unknown state "{}"'.format(desc))
            return 'k'

    def barh(self, t, newState):
        """Prepare bar from the previous state (self.t) to t. Call barh_draw when done to call matplotlib."""
        #print self.t != None, self.limitDays == None, (self.now - t).days < self.limitDays
        if self.t != None and (self.limitDays == None or (self.now - t).days < self.limitDays):
            color = self.getColor()
            width = (t - self.t).total_seconds()/(60*60*24.) # Matplotlib deals in days
            left = plt.date2num(self.t)
            self.data_barh[color].append((left, width))
            self.cumsum[self.desc] += width

        self.t = t
        self.desc = newState
        
    def barh_draw(self, ax):
        for color in sorted(self.data_barh): # the order matters since the last one will be most prominent
            ax.broken_barh(self.data_barh[color], (0, 1), color=color)

    def pie(self, ax):
        """use the cumsum to plot a pie chart"""
        x = list()
        colors = list()
        labels = list()
        for key in self.cumsum:
            x.append(self.cumsum[key])
            colors.append(self.getColor(key))
            labels.append(key.replace('_', ' ').capitalize())

        ax.pie(x, labels=labels, colors=colors, autopct='%.1f %%')

    # def runningPie(self, ax):
    #     """ use the data_barh to draw a running percentage"""
    #     data = list()
    #     for ix, color in enumerate(sorted(self.data_barh)):
    #         for left, width in self.data_barh[color]:
    #             data.append([left, ix])
    #             data.append([left+width, ix])
    #     data.sort()
    #     data = np.array(data)
    #     t, y = data[:, 0], data[:, 1]
    #     # print t, y
    #     # t_new = np.linspace(t[0], t[-1], 1024*5)
    #     # y_new = np.interp(t_new, t, y)
    #     # ax.plot(t_new, y_new+1, '.-')
    #     ax.plot(t, y+1, '.-')

def plotAll(fig, BOINC_DIR):
    filename = os.path.join(BOINC_DIR, 'time_stats_log')
    with open(filename, 'r') as f:
        p = parse(f)
        plot(fig, p, limitDays=14)
    
if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.DEBUG)
    
    import config
    
    _, _, BOINC_DIR = config.set_globals()

    fig = plt.figure()
    plotAll(fig, BOINC_DIR)

    raw_input('=== Press enter to exit ===\n')
