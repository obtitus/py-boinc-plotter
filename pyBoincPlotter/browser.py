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
Uses request library to download web content, also stores a local cache.
"""
# Standard python imports
import pickle as pk
import time
import os
import sys
import re
# Logger
import logging
logger = logging.getLogger('boinc.browser')
# Non-standard python
import requests
# This project
from project import Project
from parse import HTMLParser

# Helper functions:
def sanitizeURL(url):
    # adapted from http://stackoverflow.com/questions/7406102/create-sane-safe-filename-from-any-unsafe-string
    url = "".join([c for c in url if re.match(r'\w', c)])
    logger.debug('sanitized %s', url)
    return url

def readFile(filename):
    with open(filename, 'r') as f:
        return f.read()
join = os.path.join

class Browser_file(object):
    """Cache aware browser
    Use self.update() (which is called on init) to read in content from the cache folder
    then use self.visitURL(...) which returns the content on success or None on failure
    Cache is invalidated and removed based on age
    Using this class directly makes little sense, unless you have the entire updated internet in our cache folder
    Beware, not thread safe to update
    """
    def __init__(self, CACHE_DIR, removeOld=True):
        """removeOld should be set to False for testing"""
        self.cacheDir = CACHE_DIR
        self.removeOld = removeOld
        self.update()

    def add(self, filename):
        logger.debug('Adding %s to valid cache', filename)
        self.cache[filename] = None
    def remove(self, filename):
        logger.info('Removing old cache %s', filename)
        try:
            os.remove(filename)
        except:
            logger.exception('Unable to clean up old cach file %s', filename)

    def fileAge(self, filename):
        fileChanged = os.path.getmtime(filename)
        age = (self.now - fileChanged)/(60*60) # age of file in hours
        logger.debug('%s is %.3g h old', filename, age)
        return age
    
    def update(self):
        self.cache = dict()
        self.now = time.time()
        for filename in self.findCacheFiles(('.html', '.xml')):
            age = self.fileAge(filename)
            oldAge = 1
            if 'workunit' in filename:
                # Currently the workunit page is only used for project name, 
                # which will never change. Set to 30 days so that the file will eventually be cleaned
                oldAge = 30*24
                
            if not(self.removeOld) or age < oldAge:
                self.add(filename)
            else:
                self.remove(filename)

        for filename in self.findCacheFiles(('.jpg', '.png')): # These never expire
            self.add(filename)
        
    def findCacheFiles(self, extension):#htmlCache(self):
        for root, dirs, files in os.walk(self.cacheDir):
            for f in files:
                if f.endswith(extension):
                    yield join(root, f)

    def visitURL(self, URL, extension='.html'):
        """Returns content if the site is in cache, None otherwise."""
        filename = join(self.cacheDir, sanitizeURL(URL)) + extension
        if filename in self.cache:
            logger.debug('Getting from cache %s, %s', URL, filename)
            return readFile(filename)
        else:
            return None

class BrowserSuper(object):
    # Browser for visiting the web, use subclass to actually connect somewhere
    # Subclass must define self.URL, self.loginInfo, self.loginPage and self.name
    # or use the visitURL function directly
    def __init__(self, browser_cache):
        self.visitedPages = list()
        self.browser_cache = browser_cache # address of cache class
        self.client = requests.session()
        self.update()

    def update(self):
        c = self.try_read_cookies()
        if c != None: self.client.cookies = c
       
    def try_read_cookies(self):
        # Try to read cookies from pickle file
        try:
            filename = sanitizeURL(self.name)  + '.pickle'
            cookies = readFile(join(self.browser_cache.cacheDir, filename))
            cookies = pk.loads(cookies)
            return cookies            
        except IOError:
            logger.warning('No previous cookies found for {0}'.format(self.name))            
            return None
        except AttributeError:          # Raised when self.name is not defined, meaning we iniated BrowserSuper directly
            return None

    def writeFile(self, URL, content, extension=''):
        filename = join(self.browser_cache.cacheDir, sanitizeURL(URL)) + extension
        with open(filename, 'w') as f:
            f.write(content)
        return filename

    def authenticate(self):
        try:
            r = self.client.post(self.loginPage, data=self.loginInfo)
            logger.info('%s', r)            
        except requests.ConnectionError:
            print('Could not connect to login page')
        sessionCache = pk.dumps(self.client.cookies)
        self.writeFile(self.name, sessionCache, '.pickle')

    def visit(self, page=1):
        # Visit task page
        URL = self.URL.format(page)
        
        if URL in self.visitedPages: return ''
        self.visitedPages.append(URL)

        return self.visitURL(URL)

    def visitPage(self, page):
        return self.visitURL('http://{name}/{page}'.format(name=self.name, page=page))

    def redirected(self, request):
        """ Returns whether a redirect has been done or not """
        logger.info('%s, %s', request, request.history)
        if len(request.history) != 0:
            return True
        
        ix = request.content.find('\n')
        firstLine = request.content[:ix]
        logger.debug('First line "%s"', firstLine)
        return 'Please log in' in firstLine

    def visitURL(self, URL, recursionCall=False, extension='.html'):
        # recursionCall is used to limit recursion to 1 step
        # Extension is used for the cache for ease of debugging        
        content = self.browser_cache.visitURL(URL, extension)
        if content == None:
            logger.info('Visiting %s', URL)

            try:
                r = self.client.get(URL)
            except requests.ConnectionError:
                print('Could not connect to {0}'.format(URL))
                return ''

            if self.redirected(r):
                if not(recursionCall):
                    logger.info('Seem to have been redirected, trying to authenticate first. %s', r.url)
                    self.authenticate()
                    return self.visitURL(URL, True, extension=extension)
                else:
                    logger.error('Still being redirected, giving up. %s', r.url)
                    return ''
                
            content = r.content
            self.writeFile(URL, content, extension=extension)
        return content

    def parse(self, project=None):
        if project == None:
            project = Project(self.name)
        else:
            project = list(project) # make sure we are working on copy (easier to debug)

        content = self.visit()
        parser = HTMLParser.getParser(self.name, self)
        return parser.parse(content)

class Browser_worldcommunitygrid(BrowserSuper):
    def __init__(self, browser_cache, CONFIG):
        BrowserSuper.__init__(self, browser_cache)
        self.CONFIG = CONFIG

        self.name = 'http://www.worldcommunitygrid.org'
        self.URL = self.name +\
                   '/ms/viewBoincResults.do?filterDevice=0&filterStatus=-1&projectId=-1&pageNum={0}&sortBy=sentTime'

        self.loginInfo = {
            'settoken': 'on',
            'j_username': CONFIG.get('worldcommunitygrid.org', 'username'),
            'j_password': CONFIG.getpassword('worldcommunitygrid.org', 'username'),
            }
        self.loginPage = 'https://secure.worldcommunitygrid.org/j_security_check'

    def visitStatistics(self):
        username = self.CONFIG.get('worldcommunitygrid.org', 'username')
        code = self.CONFIG.get('worldcommunitygrid.org', 'code')
        url = self.name + "/verifyMember.do?name={0}&code={1}"
        page = self.visitURL(url.format(username, code), extension='.xml')
        return page

class Browser(BrowserSuper):
    def __init__(self, webpage_name, browser_cache, CONFIG):
        self.name = webpage_name
        BrowserSuper.__init__(self, browser_cache)
        self.webpage_name = webpage_name
        self.URL = 'http://{name}/results.php?userid={userid}'.format(
            name = webpage_name,
            userid=CONFIG.get(webpage_name, 'userid'))
        self.URL += '&offset={0}&show_names=1&state=0&appid='

        self.loginInfo = {'email_addr': CONFIG.get(webpage_name, 'username'),
                          'mode': 'Log in',
                          'next_url': 'home.php',
                          'passwd': CONFIG.getpassword(webpage_name, 'username'),
                          'stay_logged_in': 'on', # used by mindmodeling and wuprop
                          'send_cookie': 'on'}    # used by rosetta and yoyo
        self.loginPage = 'http://{0}/login_action.php'.format(webpage_name)

    def visitHome(self):
        return self.visitURL('http://{0}/home.php'.format(self.webpage_name))

    def visit(self, offset=0):
        return BrowserSuper.visit(self, offset)

class Browser_yoyo(Browser):
    def __init__(self, browser_cache, CONFIG):
        Browser.__init__(self, webpage_name='www.rechenkraft.net/yoyo',
                         browser_cache=browser_cache, CONFIG=CONFIG)
        self.loginInfo['mode'] = 'Log in with email/password'
        self.loginInfo['next_url'] = '/yoyo/home.php'


def getProjects(CONFIG, browser_cache):
    projects = list()
    for section in CONFIG.sections():
        logger.debug('section %s', section)
        # Pick subclass
        if section == 'worldcommunitygrid.org':
            browser = Browser_worldcommunitygrid(browser_cache, CONFIG)
        elif section == 'www.rechenkraft.net/yoyo':
            browser = Browser_yoyo(browser_cache, CONFIG)
        elif section == 'configuration': # Not a boinc project
            continue
        else:                   # Lets try the generic
            browser = Browser(webpage_name=section, 
                              browser_cache=browser_cache, 
                              CONFIG=CONFIG)
        yield browser.parse()

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)
    
    import config
    import util
    
    CONFIG, CACHE_DIR, _ = config.set_globals()
    browser_cache = Browser_file(CACHE_DIR)
    
    for p in getProjects(CONFIG, browser_cache):
        print p
