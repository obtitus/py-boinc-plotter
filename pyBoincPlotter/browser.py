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
Uses request library to download web content, also stores a local cache.
"""
import pickle as pk
import time
import os
import sys
import re
import logging
logger = logging.getLogger('boinc.browser')

import requests

import config

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

class Browser_cache(object):
    # Cache aware browser
    # This is just to seperate the code a little
    # Using this class directly makes no sense
    # Beware, not thread safe to initialize or update
    # Note: the entire cache folder is currently read into memory
    def __init__(self):
        self.cacheDir = config.CACHE_DIR
        self.update()

    def update(self):
        self.cache = self.read_cache()        

    def read_cache(self):
        cache = dict()
        now = time.time()
        for filename in self.findCacheFiles(('.html', '.xml')):
            fileChanged = os.path.getmtime(filename)
            age = (now - fileChanged)/(60*60) # age of file in hours
            logger.debug('%s is %s h old', filename, age)
            oldAge = 1
            if 'workunit' in filename:
                oldAge = 24*14 # Currently the workunit page is only used for project name, which will never change. Set to 14 days so that the file will eventually be cleaned
                
            if age < oldAge:
                logger.debug('Adding %s to valid cache', filename)
                cache[filename] = readFile(filename)
            else:
                logger.info('Removing old cache %s', filename)
                os.remove(filename)

        for filename in self.findCacheFiles('.jpg'): # These never expire
            logger.debug('Adding %s to valid cache', filename)            
            cache[filename] = readFile(filename)
        for filename in self.findCacheFiles('.png'): # These never expire
            logger.debug('Adding %s to valid cache', filename)            
            cache[filename] = readFile(filename)            
        return cache
        
    def findCacheFiles(self, extension):#htmlCache(self):
        for root, dirs, files in os.walk(self.cacheDir):
            for f in files:
                if f.endswith(extension):
                    yield join(root, f)

    def visitURL(self, URL, extension='.html'):
        try:
            filename = join(self.cacheDir, sanitizeURL(URL)) + extension
            content = self.cache[filename]
            logger.debug('Getting from cache %s, %s', URL, filename)
        except KeyError:                # Not found in cache
            content = None
        return content

class BrowserSuper(object):
    # Browser for visiting the web, use subclass to actually connect somewhere
    # Subclass must define self.URL, self.loginInfo, self.loginPage and self.name
    # or use the visitURL function directly
    def __init__(self):
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
        
    def authenticate(self):
        try:
            r = self.client.post(self.loginPage, data=self.loginInfo, timeout=5)
            logger.info('%s', r)            
        except requests.ConnectionError as e:
            print('Could not connect to login page. {}'.format(e))
        except requests.Timeout as e:
            print('Connection to login page timed out. {}'.format(e))
        except Exception as e:
            print('Uncaught exception for login page. {}'.format(e))
            
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

    def visitURL(self, URL, recursionCall=False, extension='.html'):
        # recursionCall is used to limit recursion to 1 step
        # Extension is used for the cache for ease of debugging        
        content = self.browser_cache.visitURL(URL, extension)
        if content == None:
            logger.info('Visiting %s', URL)

            try:
                r = self.client.get(URL, timeout=5)
            except requests.ConnectionError as e:
                print('Could not connect to {0}. {1}'.format(URL, e))
                return ''
            except requests.Timeout as e:
                print('Connection to {0}, timed out. {1}'.format(URL, e))
                return ''
            except Exception as e:
                print('Uncaught exception for {}. {}'.format(URL, e))
                return ''
            logger.info('%s, %s', r, r.history)
            firstLine = r.content.split('\n')[0].strip()
            logger.debug('First line "%s"', firstLine)
            if r.url != URL or firstLine == '<html><head><title>Please log in</title>' or '<td><h3 align="center" class="txtTitle">Please log in</h3>' in r.content: # redirected or hack for rosetta or hack for climateprediction
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

#     def visitUnvisited(self, listOfPages, projectId=-1):
#         if listOfPages == []:
#             yield self.visit(1, projectId)             # visit first page
            
#         for page in listOfPages:
#             yield self.visit(page, projectId)

class Browser_worldcommunitygrid(BrowserSuper):
    def __init__(self):
        self.name = 'worldcommunitygrid'
        BrowserSuper.__init__(self)
        self.URL = 'http://www.worldcommunitygrid.org/ms/viewBoincResults.do'
        self.URL += '?filterDevice=0&filterStatus=-1&projectId=-1&'
        self.URL += 'pageNum={0}&sortBy=sentTime'

        self.loginInfo = {
            'settoken': 'on',
            'j_username': config.CONFIG.get('worldcommunitygrid.org', 'username'),
            'j_password': config.CONFIG.getpassword('worldcommunitygrid.org', 'username'),
            }
        self.loginPage = 'https://secure.worldcommunitygrid.org/j_security_check'

    def visitStatistics(self):
        page = self.visitURL("http://www.worldcommunitygrid.org/verifyMember.do?name={0}&code={1}".format(config.CONFIG.get('worldcommunitygrid.org', 'username'),
                                                                                                        config.CONFIG.get('worldcommunitygrid.org', 'code')), extension='.xml')
        return page

class Browser(BrowserSuper):
    def __init__(self, webpageName):
        self.name = webpageName
        BrowserSuper.__init__(self)
        self.webpageName = webpageName
        self.URL = 'http://{name}/results.php?userid={userid}'.format(
            name = webpageName,
            userid=config.CONFIG.get(webpageName, 'userid'))
        self.URL += '&offset={0}&show_names=1&state=0&appid='

        self.loginInfo = {'email_addr': config.CONFIG.get(webpageName, 'username'),
                          'mode': 'Log in',
                          'next_url': 'home.php',
                          'passwd': config.CONFIG.getpassword(webpageName, 'username'),
                          'stay_logged_in': 'on', # used by mindmodeling and wuprop
                          'send_cookie': 'on'}    # used by rosetta and yoyo
        self.loginPage = 'http://{0}/login_action.php'.format(webpageName)

    def visitHome(self):
        return self.visitURL('http://{0}/home.php'.format(self.webpageName))

    def visit(self, offset=0):
        return BrowserSuper.visit(self, offset)

class Browser_yoyo(Browser):
    def __init__(self):
        Browser.__init__(self, webpageName='www.rechenkraft.net/yoyo')
        self.loginInfo['mode'] = 'Log in with email/password'
        self.loginInfo['next_url'] = '/yoyo/home.php'
        
global browser_cache
browser_cache = None                    # There should be only 1 instance of this class
def main():
    global browser_cache    
    browser_cache = Browser_cache()         # The one and only instance of this class!    
