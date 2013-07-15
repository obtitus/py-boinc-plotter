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

        try:
            showImage(ax, browser, ix,
                      value=badge.runtime, color=badge.color, url=badge.url,
                      frameon=False)
        except Exception as e:
            logger.error('Badge image failed with "%s"', e)
        
        labels.append(str(app.name))
        ix += 1

    pos = np.arange(ix)
    plt.xticks(pos+width/2, labels, rotation=17, horizontalalignment='right')
    ax.set_xlabel('Application')

    ax.set_ylabel('Runtime')
    ax.yaxis.set_major_formatter(formatter_timedelta)

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    import browser
    import project
    import boinccmd

    fig = plt.figure()

    projects = boinccmd.get_state()
    for p in projects:
        print 'URL', p.url

    CONFIG, CACHE_DIR, _ = config.set_globals()
    cache = browser.Browser_file(CACHE_DIR)
    b = browser.BrowserSuper(cache)

    p = browser.getProject('worldcommunitygrid.org', CONFIG, cache)
    print 'URL', p.url
    project.pretty_print([p])
    
    plot(fig, p, b)
    raw_input('=== Press enter to exit ===\n')
