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
import atexit
import subprocess
import readline
import shlex
import logging
logger = logging.getLogger('boinc')
# This project
from loggerSetup import loggerSetup
import config
import browser
import project
import boinccmd
import changePrefs

class Boinc(object):
    def __init__(self, parser):
        self.CONFIG, self.CACHE_DIR, self.BOINC_DIR = config.set_globals()
        self.cache = browser.Browser_file(self.CACHE_DIR)
        configureReadline(self.CONFIG.path)
        self.parse_args(parser)

        self.local_projects = dict()
        self.web_projects = dict()
        self.wuprop_projects = dict()

        self.args.update = True

    def parse_args(self, parser, args=None, namespace=None):
        #print 'parse_args called with', parser, args, namespace
        self.args = parser.parse_args(args=args, namespace=namespace)
        if args is None or len(args) == 0: # no commands where given
            self.args.update = True
        else:
            self.args.update = False

    def verbosePrintProject(self, name, proj):
        """Only print proj if verbose setting is True"""
        if self.args.verbose:
            print(name)
            project.pretty_print(proj, show_empty=True)

    def updateLocalProjects(self):
        if self.args.local:
            try:
                self.local_projects = boinccmd.get_state()
                self.verbosePrintProject('LOCAL', self.local_projects)
            except Exception as e:
                logging.error('Could not get local state, %s. Is boinc running?', e)

    def updateWebProjects(self):
        if self.args.web:
            self.cache.update() # throw out the old stuff
            self.web_projects = browser.getProjectsDict(self.CONFIG, self.cache)
            self.verbosePrintProject('WEB', self.web_projects)
            project.merge(self.local_projects, self.web_projects)
        else:
            self.web_projects = self.local_projects # so that it gets printed

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
        #print 'Logging level', loggerLevel
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
        
    def changePrefs(self):
        if self.args.prefs:
            prefs = self.args.prefs.split()
            p = changePrefs.Prefs(self.BOINC_DIR)
            for ix in range(0, len(prefs), 2): # preferences comes in pair of key, value
                prefs[ix] = prefs[ix].replace('--', '') # remove leading '--' if any
                
                if prefs[ix] == 'help':
                    parser = changePrefs.getParser(p)
                    parser.print_help() # this is slightly odd help text, but ok.
                else:
                    try:
                        logger.info('prefs %s, %s', prefs[ix], prefs[ix+1])
                        p.changePrefsFile(prefs[ix], prefs[ix+1])
                    except IndexError:
                        print("Usage error: please supply preferences as key value pairs. got %s" % prefs)
            self.args.prefs = None
            p = boinccmd.CallBoinccmd(self.BOINC_DIR, '--read_global_prefs_override')
            return p

    def startBoinc(self):
        logger.debug('self.args.boinc = %s, %s', 
                     self.args.boinc, type(self.args.boinc))
        if self.args.boinc != None:
            if self.args.boinc:
                cmd = [os.path.join(self.BOINC_DIR, 'boinc')]
                logger.info('%s', cmd)
                self.boinc = subprocess.Popen(cmd, cwd=self.BOINC_DIR)
                time.sleep(10)
                atexit.register(self.boinc.terminate)
            else:               # is false
                try:
                    self.boinc.terminate()
                except AttributeError:
                    pass
                except Exception as e:
                    print(e)
            self.args.boinc = None
        
    # def completer(self, text, state):
    #     COMMANDS = vars(self.args).keys()
    #     for cmd in COMMANDS:
    #         if cmd.startswith(text):
    #             if not state:
    #                 return cmd
    #             else:
    #                 state -= 1

def main(b):
    
    b.setLoggingLevel()
    # These do nothing if the user does ask for them
    b.addAccount()
    prefs_responce = b.changePrefs()
    boinccmd_responce = b.callBoinccmd()
    b.startBoinc()

    # Get data
    if b.args.update:
        #try:
        b.updateLocalProjects()
        b.updateWupropProjects()
        b.updateWebProjects()
        #except Exception as e:
        #    logger.exception('Uncaught exception when getting data')

        # print 'MERGED'
        project.pretty_print(b.web_projects, 
                             show_empty=b.args.verbose)
        b.plot()

        b.args.update = False   # reset for next time: todo: doesn't actually do anything

    if boinccmd_responce is not None:
        print(boinccmd_responce.communicate())
    if prefs_responce is not None:
        print(prefs_responce.communicate())

def add_switch(parser, shortName, longName, help_on, help_off='', default=True):
    if help_off == '': help_off = help_on

    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument('-'+shortName, '--'+longName, 
                           action='store_true', dest=longName,
                           default=default, help=help_on)
    exclusive.add_argument('-n'+shortName, '--no-'+longName, 
                           action='store_false', dest=longName,
                           help=help_off)
    

def configureReadline(configDir):
    # Configure readline
    # History:
    histFile = os.path.join(configDir, "history.txt")
    try: readline.read_history_file(histFile)
    except IOError: pass
    readline.set_history_length(1000)
    # Keyboard:
    # See: http://superuser.com/a/373631
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind -e")
        readline.parse_and_bind("bind '\t' rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    #readline.set_completer(completer)
    atexit.register(lambda histFile=histFile: readline.write_history_file(histFile))

def run():
    argparse.ArgumentParser.add_switch = add_switch # isn't it neat that we can change the implementation of argumentparser?
    parser = argparse.ArgumentParser(description='Boinc statistics')
    parser.add_switch('p', 'plot',
                      help_on='Use matplotlib to plot statistics and progress (default behavior)',
                      help_off='Disable plotting')
    parser.add_argument('-dmacosx', action='store_true', help='Use the macosx backend for plotting')    
    #parser.add_argument('-s', '--save', action='store_true', help='Use in combination with --plot, saves the figures to disk in the current working directory')
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument('-v', '--verbose', action='store_true', help='Sets logging level to DEBUG')
    exclusive.add_argument('-s', '--silent', action='store_true', help='Sets logging level to ERROR')    
    parser.add_argument('--add', help='Add webpage that pyBoincPlotter should track, example: "--add wuprop.boinc-af.org/"')
    parser.add_argument('--batch', help='Do not prompt for user input', action='store_false')
    parser.add_switch('w', 'web', 
                      help_on=('Allow pyBoincPlotter to connect to the internet (default behavior). '
                               'Only visits sites previously added by --add'),
                      help_off='Do not connect to the internet')
    parser.add_switch('l', 'local', 
                      help_on='Allow pyBoincPlotter to connect to local boinc client (default behavior)',
                      help_off='Do not connect to the local boinc client')
    # parser.add_switch('c', 'checkpoint', 
    #                   help_on='Show CPU time since checkpoint for active tasks.',
    #                   help_off='Hide CPU time since checkpoint for active tasks')
    parser.add_argument('--boinccmd', nargs='?', help=('Passed to the command line boinccmd, '
                                                       'pass --boinccmd=--help for more info'))
    parser.add_argument('--prefs', nargs='?', help=('Passed to the py-boinc-prefs utility '
                                                    'which changes the global_prefs_override.xml '
                                                    'and issues a read_global_prefs_override when done. '
                                                    'Pass --prefs=--help for more info'))
    parser.add_switch('b', 'boinc', 
                      help_on=('Initiate the command line version of boinc, ' 
                               'the process will be killed when py-boinc-plotter exits, '
                               'so combining with --batch makes no sense. '
                               'Default is off'),
                      help_off=('Kill any command line version of boinc controlled by py-boinc-plotter. '
                                'For interactive use after --boinc has been passed'),
                      default=False)

    b = Boinc(parser)
    main(b)

    while b.args.batch:
        user_input = input('=== Enter q, quit, e or exit to exit ===\n')
        if user_input in ('q', 'quit', 'e', 'exit'):
            break
        
        args = shlex.split(user_input)
        try:
            b.parse_args(parser, args=args, namespace=b.args)
        except SystemExit:
            pass

        main(b)

if __name__ == '__main__':
    run()
