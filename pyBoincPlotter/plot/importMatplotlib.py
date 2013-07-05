#!/usr/bin/env python
# This file is part of the py-boinc-plotter, which provides parsing and plotting of boinc statistics and badge information.
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
# 
# END LICENCE
import datetime
import logging
logger = logging.getLogger('boinc.importMatplotlib')

try:
    import numpy as np
    import matplotlib
    #matplotlib.use('module://mplh5canvas.backend_h5canvas')    
    import pylab as plt
    import matplotlib.image as mpimg
    matplotlib.rc('text', usetex=False)
    plt.ion()

    def timeTicks(x, pos):
        d = datetime.timedelta(seconds=x)
        s = str(d)
        if d.days < 0:
            d = datetime.timedelta(seconds=-x)
            s = '-' + str(d)
        return s
    formatter_timedelta = matplotlib.ticker.FuncFormatter(timeTicks)
except ImportError as e:
    print e

def dayFormat(ax, month=False):
    if month:
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=1))
    else:
        ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=1))

    # Avoid excessive numbers
    try:
        N = len(ax.get_xticks())
    except RuntimeError as e:
        logger.warning('day format error %s', e)
        N = 10000
    if N > 20:
        ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=N//15))

    if month:
        fmt = '%Y-%m'
    else:
        fmt = '%Y-%m-%d'

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(fmt))
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
