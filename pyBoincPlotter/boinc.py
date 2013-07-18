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
# Standard python
import argparse
import time
import logging
logger = logging.getLogger('boinc')
# This project
from loggerSetup import loggerSetup
import config
import browser
import project
import boinccmd

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Boinc statistics')
    parser.add_argument('-p', '--plot', action='store_true', help='Use matplotlib to plot statistics and progress')
    parser.add_argument('-dmacosx', action='store_true', help='Use the macosx backend for plotting')    
    #parser.add_argument('-s', '--save', action='store_true', help='Use in combination with --plot, saves the figures to disk in the current working directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Sets logging level to DEBUG')
    parser.add_argument('--silent', '-s', action='store_true', help='Sets logging level to ERROR')    
    parser.add_argument('--add', help='Add webpage that pyBoinc should track, example: "--add wuprop.boinc-af.org/"')
    parser.add_argument('args', nargs=argparse.REMAINDER, 
                        help='Remaining args are passed to the command line boinccmd if available, pass "--help " (with quotes for help)')
    args, boinccmd_args = parser.parse_known_args()
    boinccmd_args.extend(args.args)

    ### Make global variables ###
    CONFIG, CACHE_DIR, BOINC_DIR = config.set_globals()

    # configure logger
    loggerLevel = logging.INFO
    if args.verbose: loggerLevel = logging.DEBUG
    if args.silent: loggerLevel = logging.ERROR    
    loggerSetup(loggerLevel)    

    # Add account
    if args.add:
        CONFIG.addAccount(args.add)
        time.sleep(1)           # give boinc a chance to catch up

    # Call boinccmd
    if len(boinccmd_args) != 0:
        boinccmd_responce = boinccmd.CallBoinccmd(BOINC_DIR, boinccmd_args)
        time.sleep(1)           # give boinc a chance to catch up

    # Get data
    local_projects = boinccmd.get_state()
    # print 'LOCAL'
    # project.pretty_print(local_projects)

    cache = browser.Browser_file(CACHE_DIR)

    web_projects    = browser.getProjectsDict(CONFIG, cache)
    # print 'WEB'
    # project.pretty_print(web_projects, show_empty=True)

    wuprop_projects = browser.getProjects_wuprop(CONFIG, cache)
    # print 'WUPROP'
    # project.pretty_print(wuprop_projects, show_empty=True)
    
    project.mergeWuprop(wuprop_projects, local_projects)
    project.merge(local_projects, web_projects)
    # print 'MERGED'
    project.pretty_print(web_projects, show_empty=True)

    if len(boinccmd_args) != 0:
        print boinccmd_responce.communicate()

    # fig1 = plt.figure()
    # fig2 = plt.figure()

    # b = browser.BrowserSuper(cache)
    # plot_worldcommunitygrid(fig1, web_projects, b)
    # plot_wuprop(fig2, web_projects, b)
    # raw_input('=== Press enter to exit ===\n')


    # # Add account
    # if args.add:
    #     config.addAccount(args.add)

    # # call on boinccmd
    # boinccmd = None
    # prefs = None
    # if len(args.args) > 0:
    #     cmds = " ".join(args.args)
    #     boinccmd = task.BoincCMD(cmds)
    # if args.toggle:
    #     prefs = changePrefs.toggleCPUusage()

    # main(shouldPlot = args.plot)
    # if boinccmd: print boinccmd.communicate()
    # if prefs: print prefs.communicate()

    # prompt = '=== Enter q, quit, e or exit to exit ===\n'
    # user_input = raw_input(prompt)
    # while not(user_input in ('q', 'quit', 'e', 'exit')):
    #     boinccmd = None
    #     if user_input in ('always', 'auto', 'never'):
    #         boinccmd = task.BoincCMD('--set_run_mode {0} --set_network_mode {0}'.format(user_input))
    #     elif user_input in ('toggle', 'toggle cpu'):
    #         boinccmd = changePrefs.toggleCPUusage()
    #     elif user_input != '':
    #         boinccmd = task.BoincCMD(user_input)

    #     browser.browser_cache.update()          # Clears out any cach which have gotten too old
    #     main(shouldPlot = args.plot)
    #     if boinccmd: print boinccmd.communicate()
        
    #     user_input = raw_input(prompt)
