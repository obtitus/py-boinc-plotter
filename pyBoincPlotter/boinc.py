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
"""
Main file
"""    
# Standard python
import os
import sys
import argparse
import time
from multiprocessing import Pool
import logging
logger = logging.getLogger('boinc')
# This project
from loggerSetup import loggerSetup
import config
import browser
import project
import boinccmd

def main(parser, args=None, namespace=None):
    args, boinccmd_args = parser.parse_known_args(args=args,
                                                  namespace=namespace)
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
    if args.verbose:
        print 'LOCAL'
        project.pretty_print(local_projects)

    cache = browser.Browser_file(CACHE_DIR)

    web_projects    = browser.getProjectsDict(CONFIG, cache)
    if args.verbose:
        print 'WEB'
        project.pretty_print(web_projects, show_empty=True)

    wuprop_projects = browser.getProjects_wuprop(CONFIG, cache)
    if args.verbose:
        print 'WUPROP'
        project.pretty_print(wuprop_projects, show_empty=True)
    
    project.mergeWuprop(wuprop_projects, local_projects)
    project.merge(local_projects, web_projects)
    # print 'MERGED'
    project.pretty_print(web_projects, 
                         show_empty=args.verbose)

    if len(boinccmd_args) != 0:
        print boinccmd_responce.communicate()


    if args.plot:
        b = browser.BrowserSuper(cache)
        import plot
        # If python was sensible we could do this in parallel, 
        # but multiprocessing fails since the objects are not pickable and threads gives a warning about memory release.

        plot.plot_credits(web_projects, b)
        plot.plot_dailyTransfer(BOINC_DIR, limitDays=15)
        plot.plot_deadline(local_projects)
        plot.plot_jobLog(web_projects, BOINC_DIR)
        plot.plot_pipeline(web_projects)
        plot.plot_runtime(web_projects, b)
        plot.plot_timeStats(BOINC_DIR)

    return args

def run():
    parser = argparse.ArgumentParser(description='Boinc statistics')
    parser.add_argument('-p', '--plot', action='store_true', help='Use matplotlib to plot statistics and progress')
    parser.add_argument('-dmacosx', action='store_true', help='Use the macosx backend for plotting')    
    #parser.add_argument('-s', '--save', action='store_true', help='Use in combination with --plot, saves the figures to disk in the current working directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Sets logging level to DEBUG')
    parser.add_argument('--silent', '-s', action='store_true', help='Sets logging level to ERROR')    
    parser.add_argument('--add', help='Add webpage that pyBoinc should track, example: --add wuprop.boinc-af.org/')
    parser.add_argument('args', nargs=argparse.REMAINDER, 
                        help='Remaining args are passed to the command line boinccmd if available, pass "--help " (with quotes for help)')
    namespace = main(parser)

    while True:
        user_input = raw_input('=== Enter q, quit, e or exit to exit ===\n')
        if user_input in ('q', 'quit', 'e', 'exit'):
            break

        main(parser, 
             args=user_input.split(), namespace=namespace)

if __name__ == '__main__':
    run()
