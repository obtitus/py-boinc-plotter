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
"""Plots running time for worldcommunitygrid projects"""

# Standard python
import logging
logger = logging.getLogger('boinc.plot.runtime')
# This project
from importMatplotlib import *
from badge import Badge_wuprop
try:
    from .. import util
except ValueError:
    import util

def parse_worldcommunitygrid(projects):
    try:
        project = projects['http://www.worldcommunitygrid.org']
    except KeyError:
        logger.exception('Vops, boinc.plot.runtime.plot_worldcommunitygrid got dictionary without worldcommunitygrid, got %s. Traceback is:',
                         projects.keys())
        return
    
    data = dict()
    for key, app in sorted(project.applications.items()):
        badge = app.badge
        runtime = app.runtime.total_seconds()
        pending, running, validation = app.pendingTime()
        for prev_name in data:
            # So that "FightAIDS@Home - AutoDock" and "FightAIDS@Home - Vina" are merged with "FightAIDS@Home"
            if app.name_long.startswith(prev_name):
                data[prev_name][1] += runtime
                data[prev_name][2] += pending
                data[prev_name][3] += running
                data[prev_name][4] += validation
                break
        else:
            data[app.name_long] = [badge, runtime,
                                   pending, running, validation]
    return data
        
def plot_worldcommunitygrid(fig, browser, data):
    if data == None:
        return

    ax = fig.add_subplot(111)
    width = 0.75
    ix = 0
    labels = list()
    totalRuntime = 0
    for key in sorted(data):
        badge, runtime, pending, running, validation = data[key]

        kwargs = dict(color='k',
                      width=width)
        
        try:
            kwargs['color'] = badge.color
        except:
            pass

        height = runtime
        ax.bar(ix, height, **kwargs)

        if badge != '':
            try:
                showImage(ax, browser, ix,
                          value=badge.runtime, color=badge.color, url=badge.url,
                          frameon=False)
            except Exception as e:
                logger.error('Badge image failed with "%s"', e)

        logger.debug('app %s, pending, running, validation = %s, %s, %s', 
                     key, pending, running, validation)

        for t, alpha in ((validation, 0.5), (running, 0.25), (pending, 0.125)):
            ax.bar(ix, t, bottom=height, alpha=alpha, **kwargs)
            height += t

        totalRuntime += runtime + pending + running + validation
        labels.append(str(key))
        ix += 1

    pos = np.arange(len(labels))
    ax.set_xticks(pos+width/2)
    ax.set_xticklabels(labels, rotation=17, horizontalalignment='right')
    ax.set_xlabel('Application')

    ax.set_ylabel('Runtime')
    ax.yaxis.set_major_formatter(formatter_timedelta)

    totalRuntime = datetime.timedelta(seconds=totalRuntime)
    totalRuntime = util.timedeltaToStr(totalRuntime)
    fig.suptitle('{} worlcommunitygrid applications, total runtime {}'.format(len(labels), 
                                                                              totalRuntime))

def parse_wuprop(projects):
    applications = list()
    badges = list()             # hmm, well, there is only 1 but one can always dream
    for key, project in sorted(projects.items()):
        for key, app in sorted(project.applications.items()):
            try:
                runtime = app.statistics.wuRuntime
            except AttributeError:
                logger.debug('skipping %s since there are no wuprop stats', app.name)
                continue

            runtime_sec = runtime.total_seconds()
            color, value = Badge_wuprop.getColor(runtime_sec)
            applications.append((value, color, '{} {}'.format(project.name, app.name), app))

        for _, badge in project.badges:
            if hasattr(badge, 'isWuprop'):    # isinstance failed, see http://mail.python.org/pipermail/python-bugs-list/2005-August/029861.html
                badges.append(badge)

    # def my_cmp(app1, app2):
    #     """This shouldn't be needed"""
    #     if app1[0] != app2[0]:
    #         return cmp(app1[0], app2[0])
    #     else:
    #         return cmp(app1[2].name, app2[2].name)

    applications.sort(reverse=True)#, cmp=my_cmp)
    return applications, badges

def plot_wuprop(fig, applications, badges, browser):
    ax = fig.add_subplot(111)

    labels = list()
    width = 0.75

    totalRuntime = datetime.timedelta(0)
    for ix, data in enumerate(applications):
        badgeLine = data[0]
        color = data[1]
        label = data[2]
        app = data[3]
        stat = app.statistics

        h = stat.wuRuntime.total_seconds()
        totalRuntime += stat.wuRuntime

        color, b = Badge_wuprop.getColor(h)

        kwargs = dict(width=width, color=color)

        ax.bar(ix, h, **kwargs)

        pending = stat.wuPending.total_seconds()
        ax.bar(ix, pending, bottom=h, alpha=0.75, **kwargs)
        h += pending

        pending, running, validation = app.pendingTime(include_elapsedCPUtime=False)
        for t, alpha in ((validation, 0.5), (running, 0.25), (pending, 0.125)):
            ax.bar(ix, t, bottom=h, alpha=alpha, **kwargs)
            h += t

        labels.append(label)

        days = badgeLine*60*60
        plt.axhline(days, color=color)

    for b in badges:
        for ix, value in enumerate(b.value):
            if value != 0:
                try:
                    showImage(ax, browser, (ix+1)*20,
                              value=value*3600, url=b.url,
                              frameon=False,
                              box_alignment=(0.5, 0.5))
                except Exception as e:
                    logger.error('Badge image failed with "%s"', e)
                    
    pos = np.arange(len(labels))
    ax.set_xticks(pos+width/2)
    ax.set_xticklabels(labels, rotation=17, horizontalalignment='right')

    ax.yaxis.set_major_formatter(formatter_timedelta)

    totalRuntime = util.timedeltaToStr(totalRuntime)
    fig.suptitle('{} applications, total runtime {}'.format(len(labels), totalRuntime))

    for mark in pos[::20][1:]:
        ax.axvline(mark)
    ax.set_ylim(ymin=0)         # Negative runtime values makes no sense

def plotAll(fig1, fig2, projects, browser):
    data = parse_worldcommunitygrid(projects)
    plot_worldcommunitygrid(fig1, browser, data)

    applications, badges = parse_wuprop(projects)
    plot_wuprop(fig2, applications, badges, browser)

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    import browser
    import project
    import boinccmd

    local_projects = boinccmd.get_state()
    print 'LOCAL'
    project.pretty_print(local_projects)

    CONFIG, CACHE_DIR, _ = config.set_globals()
    cache = browser.Browser_file(CACHE_DIR)
    b = browser.BrowserSuper(cache)

    # web_p = browser.getProject('worldcommunitygrid.org', CONFIG, cache)
    # web_projects = dict()
    # web_projects[web_p.url] = web_p
    web_projects = browser.getProjectsDict(CONFIG, cache)

    wuprop_projects = browser.getProjects_wuprop(CONFIG, cache)
    print 'WUPROP'
    project.pretty_print(wuprop_projects, show_empty=True)
    
    project.mergeWuprop(wuprop_projects, local_projects)
    project.merge(local_projects, web_projects)
    print 'MERGED'
    project.pretty_print(web_projects, show_empty=True)
    #project.pretty_print(local_projects, show_empty=True)
    
    fig1 = plt.figure()
    fig2 = plt.figure()

    plotAll(fig1, fig2, web_projects, b)
    raw_input('=== Press enter to exit ===\n')
