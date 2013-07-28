# Standard python
import datetime
import xml.etree.ElementTree
from collections import defaultdict
import logging
logger = logging.getLogger('boinc.plot.dailyStatistics')
# This project
from importMatplotlib import *
from project import Project
import util
import projectColors

def parseStatistics(page, limitDays):
    tree = xml.etree.ElementTree.parse(page)

    now = datetime.datetime.now()
    data = defaultdict(list)
    for d in tree.iter('daily_statistics'):
        for child in d:
            if child.tag == 'day':
                item = float(child.text)
                item = datetime.datetime.fromtimestamp(item)
                if limitDays == None or (now - item).days < limitDays:
                    data[child.tag].append(plt.date2num(item))
                else:
                    break
            else:
                item = float(child.text)
                data[child.tag].append(float(item))
    return data

def plotStatistics(fig, data, name):
    ax1 = fig.add_subplot(211)

    try:
        color = projectColors.colors[name]
    except KeyError:
        logger.debug('Vops, no color found for %s', name)
        color = ax1._get_lines.color_cycle.next()
        projectColors.colors[name] = color

    kwargs = dict(ls='-', color=color)
    ax1.plot(data['day'], data['user_total_credit'], label='{0}'.format(name), **kwargs)

    kwargsHost = dict(marker='*', ls='-', color=color)
    ax1.plot(data['day'], data['host_total_credit'], **kwargsHost)
    ax1.set_ylabel('Total boinc credit')

    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.plot(data['day'], data['user_expavg_credit'], label='{0}'.format(name), **kwargs)

    ax2.plot(data['day'], data['host_expavg_credit'], **kwargsHost)
    ax2.legend(loc='best').draggable()

    ax2.set_xlabel('Date')
    ax2.set_ylabel('Average boinc credit')

    for ax in [ax1, ax2]:
        dayFormat(ax)

def plotAll(fig, local_projects, BOINC_DIR):
    # todo: avoid duplicate in joblog
    projects = dict()
    for p in local_projects.values():
        url = Project(url=p.url)
        projects[url.name] = p

    for url, filename in util.getLocalFiles(BOINC_DIR, 'statistics', '.xml'):
        try:
            p = Project(url=url)
            project = projects[p.name]
            label = project.name
        except KeyError:
            logger.warning('Could not find url %s in %s', url, projects)
            label = url

        with open(filename, 'r') as f:
            data = parseStatistics(f, limitDays=15)
            plotStatistics(fig, data, label)

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    import boinccmd
    
    _, _, BOINC_DIR = config.set_globals()
    local_projects = boinccmd.get_state(command='get_project_status') # Need for names

    fig = plt.figure()
    plotAll(fig, local_projects, BOINC_DIR)

    raw_input('=== Press enter to exit ===\n')
