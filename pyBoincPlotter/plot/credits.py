#!/usr/bin/env python

# Standard python
import logging
logger = logging.getLogger('boinc.badge')

# This project
from importMatplotlib import *    

def plot(fig, projects, browser):
    ax = fig.add_subplot(111)

    width = 0.75
    labels = list()
    ix = 0
    for key, project in sorted(projects.items()):
        frameon = project.name == 'rechenkraft.net_yoyo'
        for key, app in sorted(project.applications.items()):
            badge = app.badge
            if not(hasattr(badge, 'value')):
                continue

            kwargs = dict(color=badge.color, 
                          width=width)
            ax.bar(ix, app.credit, **kwargs)
            try:
                showImage(ax, browser, ix,
                          value=badge.value, color=badge.color, url=badge.url,
                          frameon=frameon)
            except Exception as e:
                logger.error('Badge image failed with "%s"', e)

            labels.append(str(app.name))
            ix += 1
    
    pos = np.arange(ix)
    plt.xticks(pos+width/2, labels, rotation=17, horizontalalignment='right')
    ax.set_xlabel('Application')
    ax.set_ylabel('Credits')

if __name__ == '__main__':
    import config
    import browser
    import project

    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)

    fig = plt.figure()

    CONFIG, CACHE_DIR, _ = config.set_globals()
    cache = browser.Browser_file(CACHE_DIR)
    b = browser.BrowserSuper(cache)

    projects = browser.getProjectsDict(CONFIG, cache)
    project.pretty_print(projects)

    plot(fig, projects, b)
    raw_input('=== Press enter to exit ===\n')
