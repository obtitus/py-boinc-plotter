#!/usr/bin/env python
import os
import xml.etree.ElementTree

import task
import config

import argparse
import logging
logger = logging.getLogger('boinc.changePrefs')

from loggerSetup import loggerSetup

class Prefs(object):
    def __init__(self, boincDir=None):
        if boincDir == None:
            self.boincDir = config.BOINC_DIR
        else:
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

def toggleCPUusage():
    try:
        p = Prefs()
        p.toggleCPUusage()

        p = task.BoincCMD('--read_global_prefs_override')
    except IOError as e:
        logger.error('Could not open prefs file due to {0}'.format(e))
        
    
if __name__ == '__main__':
    loggerSetup(logging.INFO)

    config.set_globals()

    p = Prefs()

    parser = argparse.ArgumentParser(description='Toggle boinc preferences by changing the global_prefs_override.xml file')
    #parser.add_argument('--cpu_usage_limit', type=int)
    for key, value in p.listOptions():
        name = key.replace('_', ' ').capitalize()
        parser.add_argument('--' + key, type=int, help="{name}, current value is {value}".format(name=name, value=value))
        
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
        task.BoincCMD('--read_global_prefs_override').communicate()
    #toggleCPUusage().communicate()
    
