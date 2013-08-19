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

class Boinc(object):
    def __init__(self, parser):
        self.CONFIG, self.CACHE_DIR, self.BOINC_DIR = config.set_globals()
        self.cache = browser.Browser_file(self.CACHE_DIR)
        self.parse_args(parser)

    def parse_args(self, parser, *args, **kwargs):
        args, boinccmd_args = parser.parse_known_args(*args, **kwargs)
        self.args = args
        self.args.args.extend(boinccmd_args)

    def verbosePrintProject(self, name, proj):
        """Only print proj if verbose setting is True"""
        if self.args.verbose:
            print name
            project.pretty_print(proj, show_empty=True)

    def updateLocalProjects(self):
        if not(self.args.nlocal):
            self.local_projects = boinccmd.get_state()
            self.verbosePrintProject('LOCAL', self.local_projects)

    def updateWebProjects(self):
        if not(self.args.nweb):
            self.cache.update() # throw out the old stuff
            self.web_projects = browser.getProjectsDict(self.CONFIG, self.cache)
            self.verbosePrintProject('WEB', self.web_projects)
            project.merge(self.local_projects, self.web_projects)

    def updateWupropProjects(self):
        # todo: what if wuprop is not present?
        if not(self.args.nweb):
            self.cache.update() # throw out the old stuff
            self.wuprop_projects = browser.getProjects_wuprop(self.CONFIG, self.cache)
            self.verbosePrintProject('WUPROP', self.wuprop_projects)
            project.mergeWuprop(self.wuprop_projects, 
                                self.local_projects)

    def plot(self):
        if self.args.plot:
            b = browser.BrowserSuper(self.cache)
            import plot
            # If python was sensible we could do this in parallel, 
            # but multiprocessing fails since the objects are not pickable and threads gives a warning about memory release.

            plot.plot_credits(self.web_projects, b)
            plot.plot_dailyTransfer(self.BOINC_DIR)
            plot.plot_deadline(self.local_projects)
            plot.plot_jobLog(self.web_projects, self.BOINC_DIR)
            plot.plot_pipeline(self.web_projects)
            plot.plot_runtime(self.web_projects, b)
            plot.plot_timeStats(self.BOINC_DIR)
            
    def setLoggingLevel(self, verbose, silent):
        # configure logger
        loggerLevel = logging.INFO
        if verbose: loggerLevel = logging.DEBUG
        if silent: loggerLevel = logging.ERROR    
        loggerSetup(loggerLevel)    

    def addAccount(self):
        if self.args.add:
            name = config.cleanSectionName(self.args.add)
            self.CONFIG.addAccount(name)
            self.args.add = None

    def callBoinccmd(self):
        if len(self.args.args) != 0:
            ret = boinccmd.CallBoinccmd(self.BOINC_DIR, 
                                        self.args)
            self.args.args = list()
            return ret
        
def main(b):
    
    b.addAccount()
    boinccmd_responce = b.callBoinccmd()

    # Get data
    b.updateLocalProjects()
    b.updateWupropProjects()
    b.updateWebProjects()

    # print 'MERGED'
    project.pretty_print(b.web_projects, 
                         show_empty=b.args.verbose)

    if boinccmd_responce is not None:
        print boinccmd_responce.communicate()

    b.plot()

def run():
    parser = argparse.ArgumentParser(description='Boinc statistics')
    parser.add_argument('-p', '--plot', action='store_true', help='Use matplotlib to plot statistics and progress')
    parser.add_argument('-dmacosx', action='store_true', help='Use the macosx backend for plotting')    
    #parser.add_argument('-s', '--save', action='store_true', help='Use in combination with --plot, saves the figures to disk in the current working directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Sets logging level to DEBUG')
    parser.add_argument('--silent', '-s', action='store_true', help='Sets logging level to ERROR')    
    parser.add_argument('--add', help='Add webpage that pyBoinc should track, example: --add wuprop.boinc-af.org/')
    parser.add_argument('--batch', help='Do not prompt for user input', action='store_true')
    parser.add_argument('--nweb', help='Do not connect to the internet', action='store_true')
    parser.add_argument('--nlocal', help='Do not connect to the local boinc client', action='store_true')
    parser.add_argument('args', nargs=argparse.REMAINDER, 
                        help=('Remaining args are passed'
                              'to the command line boinccmd '
                              'if available, pass "--help " (with quotes) for help'))
    b = Boinc(parser)
    main(b)

    while True:
        user_input = raw_input('=== Enter q, quit, e or exit to exit ===\n')
        if user_input in ('q', 'quit', 'e', 'exit'):
            break
        
        args=user_input.split()
        b.parse_args(parser, args=args, namespace=b.args)
        main(b)

if __name__ == '__main__':
    run()
