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
Main project class and utility plotting functions.
Project has a short and long name, some statistics and a list of tasks
"""
from __future__ import division
import re
import datetime
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import logging
logger = logging.getLogger('boinc.project')

from loggerSetup import loggerSetup
from importMatplotlib import *

class Project(object):
    # top class, contains list of status of tasks (local or web)
    # and a single web stat
    def __init__(self, name_long=None, name_short=None, active=None, stat=None):
        self.name = name_long
        self.name_short = name_short
        self.tasks = list()
        self.active = active
        self.stat = stat                # Statistics

    def __str__(self):
        name = "=== {self.name} ({self.name_short}) ===".format(self=self)
        if self.active == False:
            name = 'Completed {0}'.format(name)
        if self.stat != None:
            name += ' {0}'.format(self.stat)
            #name = '{name}\n{stat}'.format(name=name, stat=self.stat)
        s = name + '\n'
        for task in self.tasks:
            s += str(task) + '\n'

        p = self.pendingValidationTime()
        if p != datetime.timedelta(0):
            p = str(p)
            ix = p.find('.')
            if ix != -1:
                p = p[:ix]
            s += 'Total pending: {0:>41}\n'.format(p)
        return s[:-1]

    def pendingValidationTime(self):
        # Returns total time of pending validations
        p = datetime.timedelta(0)
        for task in self.tasks:
            if task.granted == 0 and task.remainingCPUtime == '0:00:00':#task.state.startswith('Pending'):
                p += task._finalCPUtime
        return p

    def pendingComputationTime(self):
        pending = datetime.timedelta(0)
        running = datetime.timedelta(0)
        for task in self.tasks:
            if task.granted == 0 and task.remainingCPUtime != '0:00:00':
                if task._currentCPUtime != datetime.timedelta(0):
                    running += task._currentCPUtime + task._remainingCPUtime
                else:
                    pending += task._currentCPUtime + task._remainingCPUtime
        return running, pending

def badgeToColor(name):
    name = name.lower()
    if name == 'bronze': name = '#8C7853'
    elif name == 'ruby': name = 'r'
    elif name == 'emerald': name = 'g'
    elif name == 'sapphire': name = 'b'
    return name
    
def plotRunningTimeByProject_worldcommunitygrid(projects, title, browser):
    fig = plt.figure('Running time by worldcommunitygrid project', figsize=(10, 8))
    fig.clf()
    plt.title(title)
    days = list() # unique list of days to mark
    
    width = 0.75
    labels = list()
    ix = 0
    for key in sorted(projects.keys()):
        stat = projects[key].stat       # statistics.Project class
        if stat == None or stat.runtime == None:
            continue
        # 'Approved' runtime
        h = stat.runtime.total_seconds()
        color = 'k'
        #badge_ix = 0
        reg = re.search('(\w+) Level Badge \((\d+) (days|years)\)', stat.badge)
        if reg:
            color = badgeToColor(reg.group(1))

            if reg.group(3) == 'years':
                year = int(reg.group(2))
                day = datetime.timedelta(years=years).total_seconds()
            elif reg.group(3) == 'days':
                day = int(reg.group(2))
                day = datetime.timedelta(days=day).total_seconds()
            else:
                logger.error('Badge level not recognized "%s", "%s"', stat.badge, reg.groups())
                continue
            
            if not(day in days): days.append([day, color])

            try:
                b = stat.badgeURL
                jpg = browser.visitURL(b, extension='.jpg')
                jpg = StringIO(jpg)
                img = mpimg.imread(jpg, format='.jpg') # may raise error due to .jpg, support for other images than .png is added by PIL
                # Add image:
                of = matplotlib.offsetbox.OffsetImage(img)
                ab = matplotlib.offsetbox.AnnotationBbox(of, (ix, day), frameon=False, box_alignment=(0, 0.5))
                plt.gca().add_artist(ab)
            except Exception as e:
                logger.error('Badge image failed with "%s"', e)

        barKwargs = dict(width=width, color=color)
        plt.bar(ix, h, **barKwargs)

        # 'Pending' runtime (not reported in or not validated)
        pending = projects[key].pendingValidationTime()
        if pending != datetime.timedelta(0):
            pending = pending.total_seconds()
            plt.bar(ix, pending, bottom=h, alpha=0.5, **barKwargs)
            h += pending

        # Waiting for computation or is being computed
        running, waiting = projects[key].pendingComputationTime()
        if running != datetime.timedelta(0):
            running = running.total_seconds()
            plt.bar(ix, running, bottom=h, alpha=0.25, **barKwargs)
            h += running
        if waiting != datetime.timedelta(0):
            waiting = waiting.total_seconds()
            plt.bar(ix, waiting, bottom=h, alpha=0.125, **barKwargs)
            h += waiting
            
        ix += 1
        labels.append(stat.name)

    pos = np.arange(ix)
    plt.xticks(pos+width/2, labels, rotation=17, horizontalalignment='right')

    for day, color in days:
        plt.axhline(day, color=color)
        
    plt.gca().yaxis.set_major_formatter(formatter_timedelta)
    return True

def plotRunningTimeByProject_wuprop(projects):
    fig = plt.figure('Running time by wuprop projects', figsize=(10, 8))
    fig.clf()
    labels = list()
    width = 0.75
    ix = 0
    badges = [[100, 'Bronze'],
              [250, 'Silver'],
              [500, 'Gold'],
              [1000, 'Ruby'],
              [2500, 'Emerald'],
              [5000, 'Sapphire']]
    daysToMark = list()
    totalRuntime = datetime.timedelta(0)
    for key in sorted(projects.keys()):
        stat = projects[key].stat       # statistics.Project class
        if stat == None or stat.wuRuntime == None:
            continue
        color = 'k'
        h = stat.wuRuntime.total_seconds()
        totalRuntime += stat.wuRuntime
        for b, c in badges:
            if h > b*60*60:
                color = badgeToColor(c);
                daysToMark.append([b, c])

        kwargs = dict(width=width, color=color)

        plt.bar(ix, h, **kwargs)
        pending = stat.wuPending.total_seconds()
        if pending != 0:
            plt.bar(ix, pending, bottom=h, alpha=0.5, **kwargs)
            h += pending

        running, waiting = projects[key].pendingComputationTime()
        if running != datetime.timedelta(0):
            running = running.total_seconds()
            plt.bar(ix, running, bottom=h, alpha=0.25, **kwargs)
            h += running
        if waiting != datetime.timedelta(0):
            waiting = waiting.total_seconds()
            plt.bar(ix, waiting, bottom=h, alpha=0.125, **kwargs)
            h += waiting

        ix += 1
        labels.append(stat.name)

    pos = np.arange(ix)
    plt.xticks(pos+width/2, labels, rotation=17, horizontalalignment='right')

    for hours, color in daysToMark:
        day = datetime.timedelta(hours=hours).total_seconds()
        plt.axhline(day, color=badgeToColor(color))

    plt.gca().yaxis.set_major_formatter(formatter_timedelta)

    plt.title('Stats for {} projects, total runtime {}'.format(len(labels), totalRuntime))

def plotCredits(projects, browser):
    fig = plt.figure('Credits by projects', figsize=(10, 8))
    fig.clf()
    ax = fig.add_subplot(111)

    badges = {'bronze': 10000,
              'silver': 100000,
              'gold': 500000,
              'master': int(1e6),
              'grandmaster': int(2e6),
              'guru': int(5e6),
              'spirit': int(10e6),
              'held': int(25e6),
              'half god' : int(50e6),
              'god': int(100e6)}
    
    width = 0.75
    labels = list()
    ix = 0
    creditsToMark = list()
    for key in sorted(projects.keys()):
        stat = projects[key].stat
        if stat == None or stat.points == None:
            continue
        h = stat.points
        kwargs = dict(color='k', width=width)

        reg = re.search('([\w\s]+) badge', stat.badge)
        if reg:
            try:
                b = badges[reg.group(1)]
                c = badgeToColor(reg.group(1))
                creditsToMark.append([b, c])
                kwargs['color'] = c
                png = browser.visitURL(stat.badgeURL, extension='.png')
                png = StringIO(png)
                img = mpimg.imread(png, format='.png')
                # Add image:
                of = matplotlib.offsetbox.OffsetImage(img)
                ab = matplotlib.offsetbox.AnnotationBbox(of, (ix, b), frameon=True, box_alignment=(0, 0.5))
                ax.add_artist(ab)
            except KeyError:
                logger.warning('badge key error %s, %s', stat.badge, reg.groups())
            except Exception as e:
                logger.error('Badge image failed with "%s"', e)                
                
        ax.bar(ix, h, **kwargs)

        ix += 1
        labels.append(stat.name)
    
    for credit, color in creditsToMark:
        plt.axhline(credit, color=color)

    pos = np.arange(ix)
    plt.xticks(pos+width/2, labels, rotation=17, horizontalalignment='right')
    #ax.set_xlabel('Project')
    ax.set_ylabel('Credits')
    
def plotTaskPipeline(projects):
    fig = plt.figure('Task pipeline', figsize=(10, 8))
    fig.clf()
    plt.title('Pipeline')
    width = 0.8
    state = ['downloading', 'ready to run', 'running', 'suspended', 'paused', 'computation completed', 'uploading', 'ready to report',
             'in progress', 'aborted', 'detached', 'error', 'no reply', 'pending validation', 'pending verification', 'valid', 'invalid', 'inconclusive', 'too late', 'waiting to send', 'other']
    # Hack, add any other states
    for key in projects:
        for task in projects[key].tasks:
            if not(task.state.lower() in state): state.append(task.state.lower())
    x = range(len(state))
    prev = np.zeros(len(state))

    N_active = len(projects)
#     for key in projects:
#         if len(projects[key].tasks) != 0:
#             N_active += 1
            
    colormap = matplotlib.cm.get_cmap('Set1')
    colors = [colormap(i) for i in np.linspace(0, 1, N_active)]
    ix_color = 0

    for key in sorted(projects.keys()):
        tasks = projects[key].tasks
        if len(tasks) != 0:
            height = np.zeros(len(state))            
            for task in tasks:
                try:
                    ix = state.index(task.state.lower())
                except ValueError:
                    logger.warning('State not found: "%s", state = "%s"', task.state, state)
                    ix = len(state)-1
                if state[ix].lower() == 'running' and task.schedularState.lower() == 'ready to start':
                    ix -= 1
                if state[ix].lower() == 'paused' and task.done():
                    ix += 3
                height[ix] += 1
            logger.debug('%s %s, prev %s', key, height, prev)
            plt.bar(x, height, bottom=prev, width=width, color=colors[ix_color], label=key)
            prev += height
        ix_color += 1

    plt.xticks(np.array(x)+width/2, state, rotation=17, horizontalalignment='right')
    plt.legend(loc='best')
    plt.xlabel('State')
    plt.ylabel('Workunit count')

def plotDeadline(projects):
    fig = plt.figure('Deadline', figsize=(10, 8))
    fig.clf()
    ax = fig.add_subplot(111)
    fig.suptitle('Time until deadline')
    
    width = 0.8
    now = datetime.datetime.today()
    norm = datetime.timedelta(days=7).total_seconds() # normalize colors to 7 days
    colormap = matplotlib.cm.get_cmap('hot')
    names = list()
    ix = 0
    for key in sorted(projects.keys()):
        for task in projects[key].tasks:
            logger.debug("%s %s %s %s", task.nameShort, task._state, task.remainingCPUtime, type(task.remainingCPUtime))
            if not(task.isWebTask()):
                r = task._remainingCPUtime.total_seconds()
                d = (task._deadline - now).total_seconds()
                c = task._currentCPUtime.total_seconds()

                p = (d - r)/norm
                color = colormap(p)
                ax.barh(ix, r, height=width, color=color)
                ax.barh(ix, 1, height=1, left=d, color=color)
                ax.barh(ix, -c, height=width, color=color)
                ax.text(x = -c, y = ix + width/2,
                        s=task.fractionDone, horizontalalignment='right', fontsize=10)
                names.append(task.nameShort.replace('_', ' '))
                ix += 1

    plt.axvline(0, color='r', ls='--')
#     plt.annotate('Estimated remaining', (0, 1), xycoords='axes fraction',
#                  xytext=(100, 0), textcoords='offset points', arrowprops=dict(arrowstyle='->'))
    plt.yticks(np.arange(len(names))+width/2, names)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(formatter_timedelta)
    plt.xlabel('Time')
    plt.ylabel('Task')

#     ticks = np.linspace(0, norm, 5)
#     ax, kw = matplotlib.colorbar.make_axes(ax)
#     matplotlib.colorbar.ColorbarBase(ax, cmap=colormap,
#                                      norm=matplotlib.colors.Normalize(vmin=min(ticks), vmax=max(ticks), clip=False),
#                                      format=formatter_timedelta,
#                                      values=ticks)

    for ix, labels in enumerate([ax.get_xticklabels(), ax.get_yticklabels()]):
        for label in labels:
            label.set_rotation(17)
            if ix == 0:
                label.set_ha('right')
            else:
                label.set_va('baseline')
    
if __name__ == '__main__':
    loggerSetup(logging.INFO)
    import statistics

    page = statistics.getPage(fromCache=True)
    if page == None:
        print 'Exiting...'
        exit(0)
    totalStats, projects = statistics.parse(page)
    plot(projects)
    plt.show()
