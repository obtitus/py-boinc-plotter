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
#!/usr/bin/env python

# Standard python imports
import os
import sys
import ConfigParser
import getpass
import logging
logger = logging.getLogger('boinc.configuration')
# Non-standard python imports
import keyring                          # TODO: optional import by storing passwords in plain text

class MyConfigParser(ConfigParser.ConfigParser):
    # Simpler config parser which automatically calls write after each key change
    def __init__(self, filename):
        self.filename = filename
        ConfigParser.ConfigParser.__init__(self)
        self.read()

    def read(self):
        ConfigParser.ConfigParser.read(self, self.filename)

    def write(self):
        with open(self.filename, 'wb') as configfile:
            ConfigParser.ConfigParser.write(self, configfile)

    def get(self, *args, **kwargs):
        try:
            return ConfigParser.ConfigParser.get(self, *args, **kwargs)
        except Exception as e:
            logger.warning("%s: %s", self.filename, e)
            return None

    def set(self, section, name, *args, **kwargs):
        try:
            ConfigParser.ConfigParser.set(self, section, name, *args, **kwargs)
        except ConfigParser.NoSectionError:
            self.add_section(section)
            # try again:
            ConfigParser.ConfigParser.set(self, section, name, *args, **kwargs)
        self.write()
        logger.debug('Written %s %s to config file %s', section, name, self.filename)

    def getpassword(self, section, name):
        username = self.get(section, name) # say the name is 'username' then username from config file will be returned
        if username != None:
            name = username
        return keyring.get_password(section, name)

    def setpassword(self, section, name, password):
        username = self.get(section, name)
        if username != None:
            name = username
        keyring.set_password(section, name, password)

from version import appName, appAuthor
from appdirs import AppDirs
appDirs = AppDirs(appName, appAuthor)

def setupCacheDir():
    cacheDir = CONFIG.get('configuration', 'cache_dir')
    if cacheDir == None:
        cacheDir = appDirs.user_cache_dir
        CONFIG.set('configuration', 'cache_dir', cacheDir)
        
    if not(os.path.isdir(cacheDir)):
        os.makedirs(cacheDir)
        if sys.platform == 'darwin':
            # Exclude folder from time machine
            cmd = ['xattr', '-w', 'com_apple_backup_excludeItem', 'com.apple.backupd', cacheDir]
            logger.info('%s', cmd)
            import subprocess
            p = subprocess.Popen(cmd)
            p.communicate()
    return cacheDir

def setupConfigFile():
    configDir = appDirs.user_data_dir
    if not(os.path.isdir(configDir)):
        os.makedirs(configDir)

    configFilename = os.path.join(configDir, 'config.txt')
    configFile = MyConfigParser(configFilename)        
    return configFile

def setupBoincDir():
    boincDir = CONFIG.get('configuration', 'boinc_dir')
    if boincDir == None:                # hmm, lets try this
        boincDir = os.environ.get('BOINC_PROJECT_DIR')
        if boincDir == None:                # okey, try something else
            if sys.platform == 'darwin':
                boincDir = '/Library/Application Support/BOINC Data'
            elif sys.platform in ('win32', 'cygwin'):
                boincDir = 'c:\Program Files\boinc'
            else:                           # Bah, lets hope its linux
                boincDir = '/var/lib/boinc-client/'
        CONFIG.set('configuration', 'boinc_dir', boincDir)
        
    return boincDir

def setupPassword(domain, additionalInfo=[], forgetOld=False):
    username = CONFIG.get(domain, 'username')
    if username == None or forgetOld:
        username = raw_input('Enter username for {0}:\n'.format(domain))
        CONFIG.set(domain, 'username', username)
        
    password = CONFIG.getpassword(domain, 'username')
    if password == None or forgetOld:
        password = getpass.getpass('Enter password for user "{0}" at {1}: '.format(username, domain))
        CONFIG.setpassword(domain, 'username', password)

    for a in additionalInfo:
        password = CONFIG.get(domain, a)
        if password == None or forgetOld:
            password = getpass.getpass('Enter {0} for user "{1}" at {2}: '.format(a, username, domain))
            CONFIG.set(domain, a, password)

global CONFIG, CACHE_DIR, BOINC_DIR
BOINC_DIR = None
CONFIG = None
CACHE_DIR = None
def set_globals():
    global CONFIG, CACHE_DIR, BOINC_DIR
    CONFIG = setupConfigFile()
    CACHE_DIR = setupCacheDir()
    BOINC_DIR = setupBoincDir()
    logger.info('Config file "%s"\nCache dir "%s"\nBoinc dir "%s"', CONFIG.filename, CACHE_DIR, BOINC_DIR)
    
def main():
    set_globals()
    setupPassword('worldcommunitygrid.org', ['code'])

def addAccount(name):
    setupPassword(name, ['userid'], forgetOld=True)
#     setupPassword('mindmodeling.org', ['userid'])
#     setupPassword('wuprop.boinc-af.org', ['userid'])
