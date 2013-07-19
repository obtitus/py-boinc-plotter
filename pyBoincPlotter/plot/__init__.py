
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
from importMatplotlib import plt
def figure(name=None):
    fig = plt.figure(name)
    fig.clf()
    return fig

import credits
import dailyTransfer
import deadline
import jobLog
import pipeline
import runtime
import timeStats

def plot_credits(projects, browser):
    fig = figure('Credits')
    credits.plot(fig, projects, browser)

def plot_dailyTransfer(BOINC_DIR, limitDays):
    fig = figure('DailyTransfer')
    filename = dailyTransfer.getFilename(BOINC_DIR)
    data = dailyTransfer.parse(filename, limitDays=limitDays)
    dailyTransfer.plot(fig, data)

def plot_deadline(local_projects):
    fig = figure('Deadline')
    deadline.plot(fig, local_projects)

def plot_jobLog(web_projects, BOINC_DIR):
    fig1 = figure('JobLog Daily')
    fig2 = figure('JobLog Monthly')

    jobLog.plotAll(fig1, fig2, web_projects, 
                        BOINC_DIR)

def plot_pipeline(web_projects):
    fig = figure('Pipeline')
    pipeline.plot(fig, web_projects)

def plot_runtime(web_projects, browser):
    fig1 = figure('Runtime Worldcommunitygrid')
    fig2 = figure('Runtime WuProp')
    runtime.plotAll(fig1, fig2, web_projects, browser)

def plot_timeStats(BOINC_DIR):
    fig = figure('TimeStats')
    timeStats.plotAll(fig, BOINC_DIR)
