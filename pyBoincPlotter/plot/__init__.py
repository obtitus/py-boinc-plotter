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
