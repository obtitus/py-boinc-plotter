#!/usr/bin/env python
"""Plots running time for worldcommunitygrid projects"""

# Standard python
import logging
logger = logging.getLogger('boinc.plot.runtime')
# This project
from importMatplotlib import *
from badge import Badge_wuprop
        
def plot_worldcommunitygrid(fig, projects, browser):
    try:
        project = projects['http://www.worldcommunitygrid.org']
    except KeyError:
        logger.exception('Vops, boinc.plot.runtime.plot_worldcommunitygrid got dictionary without worldcommunitygrid, got %s',
                         projects.keys())
        return

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

        height = app.runtime.total_seconds()
        ax.bar(ix, height, **kwargs)

        if badge != '':
            try:
                showImage(ax, browser, ix,
                          value=badge.runtime, color=badge.color, url=badge.url,
                          frameon=False)
            except Exception as e:
                logger.error('Badge image failed with "%s"', e)

        pending, running, validation = app.pendingTime()
        logger.debug('app %s, pending, running, validation = %s, %s, %s', 
                     app.name, pending, running, validation)

        for t, alpha in ((pending, 0.5), (running, 0.25), (validation, 0.125)):
            ax.bar(ix, t, bottom=height, alpha=alpha, **kwargs)
            height += t

        labels.append(str(app.name))
        ix += 1

    pos = np.arange(len(labels))
    ax.set_xticks(pos+width/2)
    ax.set_xticklabels(labels, rotation=17, horizontalalignment='right')
    ax.set_xlabel('Application')

    ax.set_ylabel('Runtime')
    ax.yaxis.set_major_formatter(formatter_timedelta)

def plot_wuprop(fig, projects, browser):
    ax = fig.add_subplot(111)

    labels = list()
    width = 0.75
    ix = 0
    badges = Badge_wuprop.badges

    daysToMark = list()
    totalRuntime = datetime.timedelta(0)
    for key, project in sorted(projects.items()):
        for key, app in sorted(project.applications.items()):
            stat = app.statistics
            try:
                stat.wuPending
            except AttributeError:
                logger.debug('skipping %s since there are no wuprop stats', app.name)
                continue

            h = stat.wuRuntime.total_seconds()
            totalRuntime += stat.wuRuntime
            
            color, b = Badge_wuprop.getColor(h)
            daysToMark.append([b, color])

            kwargs = dict(width=width, color=color)

            ax.bar(ix, h, **kwargs)

            pending = stat.wuPending.total_seconds()
            ax.bar(ix, pending, bottom=h, alpha=0.5, **kwargs)
            h += pending

            pending, running, validation = app.pendingTime()
            for t, alpha in ((running, 0.25), (validation, 0.125)):
                ax.bar(ix, t, bottom=h, alpha=alpha, **kwargs)
                h += t

            ix += 1
            labels.append(app.name)

    pos = np.arange(len(labels))
    ax.set_xticks(pos+width/2)
    ax.set_xticklabels(labels, rotation=17, horizontalalignment='right')

    for hours, color in daysToMark:
        day = datetime.timedelta(hours=hours).total_seconds()
        plt.axhline(day, color=color)

    ax.yaxis.set_major_formatter(formatter_timedelta)

    ax.set_title('Stats for {} projects, total runtime {}'.format(len(labels), totalRuntime))
    
    
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

    web_p = browser.getProject('worldcommunitygrid.org', CONFIG, cache)
    web_projects = dict()
    web_projects[web_p.url] = web_p

    wuprop_projects = browser.getProjects_wuprop(CONFIG, cache)
    print 'WUPROP'
    project.pretty_print(wuprop_projects, show_empty=True)
    
    project.mergeWuprop(wuprop_projects, local_projects)
    project.merge(local_projects, web_projects)
    print 'MERGED'
    project.pretty_print(web_projects, show_empty=True)
    
    fig1 = plt.figure()
    fig2 = plt.figure()

    plot_worldcommunitygrid(fig1, web_projects, b)
    plot_wuprop(fig2, web_projects, b)
    raw_input('=== Press enter to exit ===\n')
