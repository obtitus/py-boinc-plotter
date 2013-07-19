#!/usr/bin/env python
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
    now = datetime.datetime.now()
    
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
            power.barh(ax0, t, newState)
        elif desc.startswith('net'):
            newState = desc[len('net_'):]
            net.barh(ax1, t, newState)
        elif desc.startswith('proc'):
            newState = desc[len('proc_'):]
            proc.barh(ax2, t, newState)
        else:
            logger.warning('plotTimeStats, did not recognize "{}" as description'.format(desc))

    # Draw current state to now
    for ix, item in enumerate([power, net, proc]):
        item.barh(axes[ix], now, '')
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
        self.now = datetime.datetime.now()
        self.limitDays = limitDays

    def getColor(self, desc=None):
        if desc == None: desc = self.desc
        try:
            return self.states[desc]
        except KeyError:
            logger.warning('plotTimeStats unknown state "{}"'.format(desc))
            return 'k'

    def barh(self, ax, t, newState):
        """Draw a bar from the previous state (self.t) to t"""
        #print self.t != None, self.limitDays == None, (self.now - t).days < self.limitDays
        if self.t != None and (self.limitDays == None or (self.now - t).days < self.limitDays):
            color = self.getColor()
            width = (t - self.t).total_seconds()/(60*60*24.) # Matplotlib deals in days
            left = plt.date2num(self.t)
            # logger.debug('drawing a bar "%s" from %s, of length %.3g to %s', 
            #              self.desc, plt.num2date(left), width*24, plt.num2date(left+width))
            ax.barh(bottom=0, width=width, 
                    left=left, height=1, color=color, linewidth=0)

            self.cumsum[self.desc] += width # todo substract outside wanted range

        self.update(t, newState)

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
