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
"""
Main file
"""

# Standard python imports
import sys
import re
from datetime import datetime
import argparse
import logging
logger = logging.getLogger('boinc')

# Project import
from loggerSetup import loggerSetup
import task
import parse
import statistics
import browser
import async
import project
import changePrefs
import config

def getCMDstate():
    p = task.BoincCMD()
    content = p.communicate()
    parser = parse.CMDparser()
    if content != None:
        parser.feed(content)
    return parser

def getCCstate():
    p = task.BoincCMD(argument='--get_cc_status')
    content = p.communicate()
    return content

def getWebstate():
    # TODO: make async
    b = browser.Browser_worldcommunitygrid()
    parser = parse.HTMLParser_worldcommunitygrid(b)
    content = b.visit()
    parser.feed(content)

    for section in config.CONFIG.sections():
        if section in ['configuration', 'worldcommunitygrid.org']:
            continue
        # Pick browser
        if 'rechenkraft.net/yoyo' in section:
            b = browser.Browser_yoyo()
        else:
            b = browser.Browser(section)
        # todo: similar with parser
        parser = parse.HTMLParser_boinc(browser=b, projects=parser.projects, tasks=parser.tasks)
        content = b.visit()
        parser.feed(content)


    return parser

def getWebstat(shouldPlot=False):
    b = browser.Browser_worldcommunitygrid()
    page = b.visitStatistics()
    if page == '': return None, None
    totalStats, projects = statistics.parse(page)

    for section in config.CONFIG.sections():
        if section in ['configuration', 'worldcommunitygrid.org']:
            continue
        b = browser.Browser(section)
        page = b.visitHome()
        parser = statistics.HTMLParser_boinchome()
        wuprop = section == 'wuprop.boinc-af.org'
        parser.feed(page, wuprop=wuprop)
        logger.debug('Visited section %s, got %s', section, parser.projects)

        for k in parser.projects:
            if not(projects.has_key(k)):
                projects[k] = parser.projects[k]

            if parser.projects[k].wuRuntime != None:
                projects[k].wuRuntime = parser.projects[k].wuRuntime
                projects[k].wuPending = parser.projects[k].wuPending

            if projects[k].points == None and parser.projects[k].points != None:
               projects[k].points = parser.projects[k].points
               projects[k].results = parser.projects[k].results
               projects[k].badge = parser.projects[k].badge
               projects[k].badgeURL = parser.projects[k].badgeURL

    return totalStats, projects

def findStat(projectDict_stat, key):
    logger.debug('Trying to find stat for "%s"', key)
    if projectDict_stat.has_key(key):
        return projectDict_stat[key]
    # Hack:
    # if not lets check for similarities
    reg = re.compile(key + ' \(\w*\)')
    for k in projectDict_stat.keys():
        if key.startswith(k) or re.match(reg, k):
            ret = projectDict_stat[k]
            del projectDict_stat[k]
            return ret
    else:
        logger.debug('Failed to find %s, in %s', key, projectDict_stat)
    return None
    
def intertwineData(projectDict, projectDict_stat, localList, webList):
    # Fill out the project information from the local and web information given
    # First, figure out local and web list link
    logger.debug('intertwine called with ProjectDict: "%s"\n, ProjectDict_stat: "%s"\n , localList: "%s", webList: "%s"', projectDict, projectDict_stat, localList, webList)
    s = ''
    try:
        h = localList[0].header
        s += localList[0].header + '\n'
        s += '-'*len(h) + '\n'
    except Exception: pass

    if projectDict_stat == None:
        projectDict_stat = dict() # avoids some crashes
    
    notFound = 'Project name not found'
    for localTask in localList:         # For each local
        logger.debug('Trying to find %s', localTask.name)
        ix = 0
        found = False
        while ix < len(webList):        # For each web
            #print 'Is "%s" == "%s"' % (localTask.name, webList[ix].name)
            if localTask.name.startswith(webList[ix].name): # found
                found = True
                projectDict[webList[ix].projectName].tasks.append(localTask)
                del webList[ix]
                break
            else:
                ix += 1
        if found == False:              # We can't determine project name, so add a new project called notFound (happends when there is no internett connection or when the cache is outdated)
            logger.debug('Failed to find %s in webList', localTask.name)
            if not(projectDict.has_key(notFound)):
                projectDict[notFound] = project.Project(name_long=notFound, name_short="not found")
            projectDict[notFound].tasks.append(localTask)
            #s += str(localTask) + '\tProject name not found' + '\n'

    for remaining in webList:
        if remaining.name != 'ResultName':
            projectDict[remaining.projectName].tasks.append(remaining)

    for key in sorted(projectDict):
        stat = findStat(projectDict_stat, key)
        projectDict[key].stat = stat    # Add stat
        logger.debug('Adding stat "%s" to project %s', stat, key)
        if len(projectDict[key].tasks) != 0:
            s += str(projectDict[key]) + '\n' # Add to printout

    # If the only information we have is statistics, remember to add that
    for key in sorted(projectDict_stat):
        if findStat(projectDict, key) == None:
            projectDict[key] = project.Project(stat=projectDict_stat[key])

    return s, projectDict

def printState(shouldPlot=False):
    # Main function, bringing all the information togheter
    
    # Async part
    cc_state = async.Async(getCCstate)
    parser_local = async.Async(getCMDstate)
    parser_web = async.Async(getWebstate)
    stat = async.Async(getWebstat, shouldPlot)

    # Join
    cc_state = cc_state.ret
    totalStats, projects_stat = stat.ret
    parser_local = parser_local.ret
    parser_web = parser_web.ret

    projects, projectDict = intertwineData(parser_web.projects, projects_stat, parser_local.tasks, parser_web.tasks)
    # Present collected data to the user
    print cc_state
    print parser_local.info
    print totalStats
    print projects
    
    # plot
    if shouldPlot:
        project.plotTaskPipeline(projectDict)
        project.plotDeadline(projectDict)
        if totalStats != None:
            b = browser.BrowserSuper()
            project.plotRunningTimeByProject_worldcommunitygrid(projectDict, totalStats.runtime, browser=b)
            if 'wuprop.boinc-af.org' in config.CONFIG.sections():            
                project.plotRunningTimeByProject_wuprop(projectDict)
            project.plotCredits(projectDict, browser=b)

def main(shouldPlot):
    printState(shouldPlot=shouldPlot)
    if shouldPlot:
        import statistics_plot
        statistics_plot.main()
    
def run():
    datetime.strptime("", "") # avoids threading bug, see http://bugs.python.org/issue7980
    parser = argparse.ArgumentParser(description='Boinc statistics for world community grid')
    parser.add_argument('-p', '--plot', action='store_true', help='Use matplotlib to plot statistics and progress')
    parser.add_argument('-dmacosx', action='store_true', help='Use the macosx backend for plotting')    
    #parser.add_argument('-s', '--save', action='store_true', help='Use in combination with --plot, saves the figures to disk in the current working directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Sets logging level to DEBUG')
    parser.add_argument('--silent', '-s', action='store_true', help='Sets logging level to ERROR')    
    parser.add_argument('--always', action='store_true', help='Passes "--set_run_mode always --set_network_mode always" to boinccmd')
    parser.add_argument('--auto', action='store_true', help='Passes "--set_run_mode auto --set_network_mode auto" to boinccmd')
    parser.add_argument('--never', action='store_true', help='Passes "--set_run_mode never --set_network_mode never" to boinccmd')
    parser.add_argument('--toggle', action='store_true', help='Toggles CPU usage of boinc. See changePrefs.py for details')
    parser.add_argument('--add', help='Add account, example: "--add wuprop.boinc-af.org/"')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Remaining args are passed to boinccmd')
    args = parser.parse_args()

    # If you pass in multiple of these, say --always --never, then let boinccmd deal with the ambiguity
    if args.always:
        args.args.extend(['--set_run_mode always', '--set_network_mode always'])
    if args.auto:
        args.args.extend(['--set_run_mode auto', '--set_network_mode auto'])
    if args.never:
        args.args.extend(['--set_run_mode never', '--set_network_mode never'])

    ### Make global variables ###
    # configure logger
    loggerLevel = logging.INFO
    if args.verbose: loggerLevel = logging.DEBUG
    if args.silent: loggerLevel = logging.ERROR    
    loggerSetup(loggerLevel)    

    config.main()
    browser.main()
    ###

    # Add account
    if args.add:
        config.addAccount(args.add)

    # call on boinccmd
    boinccmd = None
    prefs = None
    if len(args.args) > 0:
        cmds = " ".join(args.args)
        boinccmd = task.BoincCMD(cmds)
    if args.toggle:
        prefs = changePrefs.toggleCPUusage()

    main(shouldPlot = args.plot)
    if boinccmd: print boinccmd.communicate()
    if prefs: print prefs.communicate()

    prompt = '=== Enter q, quit, e or exit to exit ===\n'
    user_input = raw_input(prompt)
    while not(user_input in ('q', 'quit', 'e', 'exit')):
        boinccmd = None
        if user_input in ('always', 'auto', 'never'):
            boinccmd = task.BoincCMD('--set_run_mode {0} --set_network_mode {0}'.format(user_input))
        elif user_input in ('toggle', 'toggle cpu'):
            boinccmd = changePrefs.toggleCPUusage()
        elif user_input != '':
            boinccmd = task.BoincCMD(user_input)

        browser.browser_cache.update()          # Clears out any cach which have gotten too old
        main(shouldPlot = args.plot)
        if boinccmd: print boinccmd.communicate()
        
        user_input = raw_input(prompt)

if __name__ == '__main__':
    run()
