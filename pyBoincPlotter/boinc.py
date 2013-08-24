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
        self.args = parser.parse_args(*args, **kwargs)

    def verbosePrintProject(self, name, proj):
        """Only print proj if verbose setting is True"""
        if self.args.verbose:
            print name
            project.pretty_print(proj, show_empty=True)

    def updateLocalProjects(self):
        if self.args.local:
            self.local_projects = boinccmd.get_state()
            self.verbosePrintProject('LOCAL', self.local_projects)

    def updateWebProjects(self):
        if self.args.web:
            self.cache.update() # throw out the old stuff
            self.web_projects = browser.getProjectsDict(self.CONFIG, self.cache)
            self.verbosePrintProject('WEB', self.web_projects)
            project.merge(self.local_projects, self.web_projects)

    def updateWupropProjects(self):
        # todo: what if wuprop is not present?
        if self.args.web:
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
            
    def setLoggingLevel(self):
        # configure logger
        loggerLevel = logging.INFO
        if self.args.verbose: loggerLevel = logging.DEBUG
        if self.args.silent: loggerLevel = logging.ERROR    
        loggerSetup(loggerLevel)    

    def addAccount(self):
        if self.args.add:
            name = config.cleanSectionName(self.args.add)
            self.CONFIG.addAccount(name)
            self.args.add = None

    def callBoinccmd(self):
        if self.args.boinccmd:
            ret = boinccmd.CallBoinccmd(self.BOINC_DIR, 
                                        self.args.boinccmd)
            self.args.boinccmd = None
            return ret
        
def main(b):
    
    b.addAccount()
    b.setLoggingLevel()
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

def add_switch(parser, shortName, longName, help_on, help_off='', default=True):
    if help_off == '': help_off = help_on

    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument('-'+shortName, '--'+longName, 
                           action='store_true', dest=longName,
                           default=default, help=help_on)
    exclusive.add_argument('-n'+shortName, '--no-'+longName, 
                           action='store_false', dest=longName,
                           help=help_off)

def run():
    argparse.ArgumentParser.add_switch = add_switch # isn't it neat that we can change the implementation of argumentparser?
    parser = argparse.ArgumentParser(description='Boinc statistics')
    parser.add_switch('p', 'plot',
                      help_on='Use matplotlib to plot statistics and progress',
                      help_off='Disable plotting')
    parser.add_argument('-dmacosx', action='store_true', help='Use the macosx backend for plotting')    
    #parser.add_argument('-s', '--save', action='store_true', help='Use in combination with --plot, saves the figures to disk in the current working directory')
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument('-v', '--verbose', action='store_true', help='Sets logging level to DEBUG')
    exclusive.add_argument('-s', '--silent', action='store_true', help='Sets logging level to ERROR')    
    parser.add_argument('--add', help='Add webpage that pyBoincPlotter should track, example: --add wuprop.boinc-af.org/')
    parser.add_argument('--batch', help='Do not prompt for user input', action='store_false')
    parser.add_switch('w', 'web', 
                      help_on='Allow pyBoincPlotter to connect to the internet',
                      help_off='Do not connect to the internet')
    parser.add_switch('l', 'local', 
                      help_on='Allow pyBoincPlotter to connect to local boinc client',
                      help_off='Do not connect to the local boinc client')
    
    parser.add_argument('--boinccmd', nargs='?', help=('Passed to the command line boinccmd'
                                                       'if available, pass --boinccmd=--help for more info'))
    b = Boinc(parser)
    main(b)

    while b.args.batch:
        user_input = raw_input('=== Enter q, quit, e or exit to exit ===\n')
        if user_input in ('q', 'quit', 'e', 'exit'):
            break
        
        args=user_input.split()
        b.parse_args(parser, args=args, namespace=b.args)
        main(b)

if __name__ == '__main__':
    run()
