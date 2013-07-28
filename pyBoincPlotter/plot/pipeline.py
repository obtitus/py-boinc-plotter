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
"""Shows number of tasks in each state"""

# Standard python
import logging
logger = logging.getLogger('boinc.plot.pipeline')
# This project
from importMatplotlib import *
try:
    from ..task import Task
except ValueError:
    from task import Task

def plot(fig, projects):
    states = ['in progress', 
              'downloading', 'ready to run', 'running', 'suspended', 'paused', 
              'computation completed', 'uploading', 'ready to report', 
              'pending validation', 'pending verification', 
              'valid', 'invalid', 'inconclusive', 'too late', 'unknown']

    apps = list()
    for p in projects.values():
        for app in p.applications.values():
            apps.append(app)

            for task in app.tasks:
                if task.state_str not in states:
                    logger.debug('Adding state %s', task.state_str)
                    states.append(task.state_str)

    colormap = matplotlib.cm.get_cmap('Set1')
    colors = [colormap(i) for i in np.linspace(0, 1, len(apps))]

    ax = fig.add_subplot(111)
    width = 0.75
    bottom = np.zeros(len(states)) # TODO: I guess we can manage without numpy
    x = np.arange(len(states))

    for ix_app, app in enumerate(apps):
        if len(app.tasks) == 0:
            continue

        height = np.zeros(len(states))
        for task in app.tasks:
            ix = states.index(task.state_str)
            height[ix] += 1
        
        ax.bar(x, height, bottom=bottom, 
               color=colors[ix_app], width=width,
               label=app.name)
            
        bottom += height

    plt.xticks(x+width/2, states, rotation=17, horizontalalignment='right')
    ax.set_xlabel('State')

    ax.set_ylabel('Count')
    leg = ax.legend(loc='upper left')
    leg.draw_frame(False)

    fig.suptitle("Showing state of {:.0f} tasks".format(sum(bottom)))

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    import browser
    import project
    import boinccmd

    fig = plt.figure()

    local_projects = boinccmd.get_state()
    # print 'LOCAL'
    # project.pretty_print(local_projects)

    CONFIG, CACHE_DIR, _ = config.set_globals()
    cache = browser.Browser_file(CACHE_DIR)
    b = browser.BrowserSuper(cache)

    web_projects = browser.getProjectsDict(CONFIG, cache)
    
    project.merge(local_projects, web_projects)
    project.pretty_print(web_projects)
    
    plot(fig, web_projects)
    raw_input('=== Press enter to exit ===\n')
