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
        frameon = project.url != 'http://www.primegrid.com'
        for app, badge in project.badges:
            print app, badge
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
