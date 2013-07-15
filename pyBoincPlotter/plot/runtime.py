#!/usr/bin/env python
"""Plots running time for worldcommunitygrid projects"""

# Standard python
import logging
logger = logging.getLogger('boinc.plot.runtime')
# This project
from importMatplotlib import *

def plot(fig, project, browser):
    ax = fig.add_subplot(111)
    width = 0.75
    ix = 0
    labels = list()
    for key in sorted(project.applications):
        app = project.applications[key]
        badge = app.badge
        kwargs = dict(color='k',
                      width=width)
        
        try:
            kwargs['color'] = badge.color
        except:
            pass

        logger.debug('runtime %s, type(app.runtime) %s', app.runtime, type(app.runtime))
        ax.bar(ix, app.runtime.total_seconds(), **kwargs)

        labels.append(str(app.name))
        ix += 1

        if badge == '':
            continue

        try:
            showImage(ax, browser, ix-1,
                      value=badge.runtime, color=badge.color, url=badge.url,
                      frameon=False)
        except Exception as e:
            logger.error('Badge image failed with "%s"', e)
        
    pos = np.arange(ix)
    plt.xticks(pos+width/2, labels, rotation=17, horizontalalignment='right')
    ax.set_xlabel('Application')

    ax.set_ylabel('Runtime')
    ax.yaxis.set_major_formatter(formatter_timedelta)

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.DEBUG)
    
    import config
    import browser
    import project
    import boinccmd

    fig = plt.figure()

    local_projects = boinccmd.get_state()
    print 'LOCAL'
    project.pretty_print(local_projects)

    CONFIG, CACHE_DIR, _ = config.set_globals()
    cache = browser.Browser_file(CACHE_DIR)
    b = browser.BrowserSuper(cache)

    web_p = browser.getProject('worldcommunitygrid.org', CONFIG, cache)
    
    web_projects = dict()
    web_projects[web_p.url] = web_p
    
    project.merge(local_projects, web_projects)
    print 'MERGED'
    print web_projects
    project.pretty_print(web_projects)
    
    plot(fig, web_p, b)
    raw_input('=== Press enter to exit ===\n')
