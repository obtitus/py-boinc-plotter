#!/usr/bin/env python
"""Shows number of tasks in each state"""

# Standard python
import logging
logger = logging.getLogger('boinc.plot.pipeline')
# This project
from importMatplotlib import *
from task import Task

def plot(fig, projects):
    states = Task.desc_state
    states.extend(['in progress', 
                   'aborted', 'detached', 'error', 'no reply', 
                   'pending validation', 'pending verification', 
                   'valid', 'invalid', 'inconclusive', 'too late', 
                   'waiting to send'])

    apps = list()
    for p in projects.values():
        for app in p.applications.values():
            apps.append(app)

            for task in app.tasks:
                if task.state_str not in states:
                    states.append(task.state)


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
    ax.legend()

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
