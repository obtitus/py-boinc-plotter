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

import os
import xml.etree.ElementTree

import config
import boinccmd

import argparse
import logging
logger = logging.getLogger('boinc.changePrefs')

from loggerSetup import loggerSetup

class Prefs(object):
    def __init__(self, boincDir):
        self.boincDir = boincDir

        self.filename = os.path.join(self.boincDir, 'global_prefs_override.xml')
        with open(self.filename, 'r') as f:
            self.tree = xml.etree.ElementTree.parse(f)

    def listOptions(self):
        # Read the prefs file and yield name and value for each entry
        for item in self.tree.getroot():
            yield item.tag, item.text
    def changePrefsFile(self, name, newValue):
        e = self.tree.find(name)
        e.text = str(newValue)
        self.tree.write(self.filename)

    def toggleCPUusage(self):
        # Toggles 'cpu_usage_limit' between 20 and 100 percent
        name = 'cpu_usage_limit'
        e = self.tree.find(name)
        current = float(e.text)
        if abs(current - 100) < 1:      # current == 100
            logger.info('Setting cpu limit to %d', 20)
            self.changePrefsFile(name, 20)
        else:
            logger.info('Setting cpu limit to %d', 100)
            self.changePrefsFile(name, 100)

        
def changePrefs(BOINC_DIR, a, value=None):
    # Convenient function for changing a preference
    # If value is None simply return current value
    prefs = Prefs(BOINC_DIR)
    if value != None:
        prefs.changePrefsFile(a, value)
        p = boinccmd.CallBoinccmd(BOINC_DIR, '--read_global_prefs_override')
        p.communicate()
    return prefs.tree.find(a).text

def getParser(p):
    parser = argparse.ArgumentParser(description='Toggle boinc preferences by changing the global_prefs_override.xml file')
    #parser.add_argument('--cpu_usage_limit', type=int)
    for key, value in p.listOptions():
        name = key.replace('_', ' ').capitalize()
        parser.add_argument('--' + key, type=int, help="{name}, current value is {value}".format(name=name, value=value))
    return parser

def run():
    CONFIG, CACHE_DIR, BOINC_DIR = config.set_globals()

    p = Prefs(BOINC_DIR)

    parser = getParser(p)
    args = parser.parse_args()

    # For each argument:
    changed = False
    for a in args.__dict__:
        value = args.__dict__[a]
        if value != None:
            p.changePrefsFile(a, value)
            changed = True

    if changed:
        # Upate
        boinccmd.CallBoinccmd(BOINC_DIR, '--read_global_prefs_override').communicate()
    #toggleCPUusage().communicate()
    
if __name__ == '__main__':
    loggerSetup(logging.INFO)
    run()
