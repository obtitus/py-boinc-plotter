#!/usr/bin/env python
# Standard python
import datetime
import logging
logger = logging.getLogger('boinc.plot.deadline')
# This project
from importMatplotlib import *

def plot(fig, projects):
    ax = fig.add_subplot(111)
    
    width = 0.8
    now = datetime.datetime.today()
    norm = datetime.timedelta(days=7).total_seconds() # normalize colors to 7 days
    colormap = matplotlib.cm.get_cmap('hot')
    names = list()
    ix = 0
    totalRemaining = datetime.timedelta(0)
    for key, p in sorted(projects.items()):
        for task in p.tasks():
            r = task.remainingCPUtime.total_seconds()
            d = (task.deadline - now).total_seconds()
            c = task.elapsedCPUtime.total_seconds()

            totalRemaining += task.remainingCPUtime

            p = (d - r)/norm
            color = colormap(p)
            ax.barh(ix, r, height=width, color=color)
            ax.barh(ix, 1, height=1, left=d, color=color)
            ax.barh(ix, -c, height=width, color=color)
            if task.state_str == 'running': color = 'k'
            elif task.state_str == 'ready to report': color='g'
            else: color = 'b'
            ax.text(x = -c, y = ix + width/2,
                    s=task.fractionDone_str, horizontalalignment='right', fontsize=10, color=color)
            names.append(task.nameShort_str.replace('_', ' '))
            ix += 1

    plt.axvline(0, color='r', ls='--')
    plt.yticks(np.arange(len(names))+width/2, names)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(formatter_timedelta)

    fig.suptitle('Time until deadline\nTotal work remaining %s' % totalRemaining)
    ax.set_xlabel('Time')
    ax.set_ylabel('Task')

    for ix, labels in enumerate([ax.get_xticklabels(), ax.get_yticklabels()]):
        for label in labels:
            label.set_rotation(17)
            if ix == 0:
                label.set_ha('right')
            else:
                label.set_va('baseline')

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)

    import boinccmd
    import project

    projects = boinccmd.get_state()
    project.pretty_print(projects)

    fig1 = plt.figure()
    plot(fig1, projects)

    raw_input('=== Press enter to exit ===\n')
