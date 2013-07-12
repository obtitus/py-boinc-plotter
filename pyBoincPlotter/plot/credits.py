#!/usr/bin/env python

# Standard python
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import logging
logger = logging.getLogger('boinc.badge')

# This project
from importMatplotlib import *

def showImage(ax, ix, badge, browser):
    try:
        value = badge.value
        color = badge.color
        url = badge.url
        extension = url[-4:]

        ax.axhline(value, color=color)
        png = browser.visitURL(url, extension=extension)
        png = StringIO(png)
        img = mpimg.imread(png, format=extension)
        # Add image:
        of = matplotlib.offsetbox.OffsetImage(img)
        ab = matplotlib.offsetbox.AnnotationBbox(of, (ix, value), 
                                                 frameon=False, box_alignment=(0, 0.5))
        ax.add_artist(ab)
    except Exception as e:
        logger.error('Badge image failed with "%s"', e)
    

def plot(fig, projects, browser):
    ax = fig.add_subplot(111)

    width = 0.75
    labels = list()
    ix = 0
    for project in projects:
        for key in sorted(project.applications):
            app = project.applications[key]
            badge = app.badge
            if badge == '':
                continue

            kwargs = dict(color=badge.color, 
                          width=width)
            ax.bar(ix, app.credit, **kwargs)
            showImage(ax, ix, badge, browser)

            labels.append(str(app.name))
            ix += 1
    
    pos = np.arange(ix)
    plt.xticks(pos+width/2, labels, rotation=17, horizontalalignment='right')
    #ax.set_xlabel('Project')
    ax.set_ylabel('Credits')

if __name__ == '__main__':
    import config
    import browser
    import project

    fig = plt.figure()

    CONFIG, CACHE_DIR, BOINC_DIR = config.set_globals()
    cache = browser.Browser_file(CACHE_DIR)
    b = browser.BrowserSuper(cache)
    projects = browser.getProjects(CONFIG, cache)
    plot(fig, projects, b)
    raw_input('=== Press enter to exit ===\n')
