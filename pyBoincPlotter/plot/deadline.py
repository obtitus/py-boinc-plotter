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
# Standard python
import datetime
import logging
logger = logging.getLogger('boinc.plot.deadline')
# This project
from importMatplotlib import *
try:
    from .. import util
except ValueError:
    import util

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
            try:
                r = task.remainingCPUtime.total_seconds()
                d = (task.deadline - now).total_seconds()
                c = task.elapsedCPUtime.total_seconds()
            except TypeError:
                continue

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

    fig.suptitle('Time until deadline\nTotal work remaining %s' % util.timedeltaToStr(totalRemaining))
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
