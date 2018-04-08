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
# Standard python imports
import pickle as pk
import time
import os
import sys
import re
import argparse
import logging
logger = logging.getLogger('boinc.browser')
# Non-standard python
import requests
# This project
from project import Project, pretty_print
from parse import HTMLParser
import async

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
    def __init__(self, CACHE_DIR, removeOld=True, removeOldAge=1):
        """removeOld should be set to False for testing"""
        self.removeOldAge = removeOldAge
        self.cacheDir = CACHE_DIR
        self.removeOld = removeOld
        self.update()

    def add(self, filename):
        #logger.debug('Adding %s to valid cache', filename)
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
        #logger.debug('%s is %.3g h old', filename, age)
        return age
    
    def update(self):
        self.cache = dict()
        self.now = time.time()
        for filename in self.findCacheFiles(('.html', '.xml', '.json')):
            age = self.fileAge(filename)
            oldAge = self.removeOldAge
            # if 'workunit' in filename:
            #     # Currently the workunit page is only used for project name, 
            #     # which will never change. Set to 30 days so that the file will eventually be cleaned
            #     oldAge = 30*24
            if 'show_host_detail' in filename:
                # host page is unlikely to change that often
                # Set to 90 days so that the file will eventually be cleaned
                oldAge = 90*24
                
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

    def removeURL(self, URL, extension='.html'):
        """If you visit a task page that errors out, 
        call this to remove the page from cache to try again."""
        filename = join(self.cacheDir, sanitizeURL(URL)) + extension
        self.remove(filename)

class BrowserSuper(object):
    # Browser for visiting the web, use subclass to actually connect somewhere
    # Subclass must define self.URL, self.loginInfo, self.loginPage and self.section
    # or use the visitURL function directly
    def __init__(self, browser_cache):
        self.visitedPages = list()
        self.browser_cache = browser_cache # address of cache class
        self.removeURL = self.browser_cache.removeURL
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
        self.browser_cache.add(filename)
        return filename

    def authenticate(self):
        try:
            #print self.loginInfo
            r = self.client.post(self.loginPage, data=self.loginInfo, timeout=5)
            logger.info('Authenticate responce "%s"', r)
            #print r.content
        except requests.ConnectionError as e:
            print('Could not connect to login page. {}'.format(e))
        except requests.Timeout as e:
            print('Connection to login page timed out. {}'.format(e))
        except Exception as e:
            print('Uncaught exception for login page. {}'.format(e))

        sessionCache = pk.dumps(self.client.cookies)
        self.writeFile(self.name, sessionCache, '.pickle')

    def visit(self, page=1, **kwargs):
        # Visit task page
        URL = self.URL.format(page)
        
        if URL in self.visitedPages: return ''
        self.visitedPages.append(URL)

        return self.visitURL(URL, **kwargs)

    def visitPage(self, page, **kwargs):
        return self.visitURL('{name}/{page}'.format(name=self.name, page=page), **kwargs)

    def redirected(self, request):
        """ Returns whether a redirect has been done or not """
        logger.info('response and history "%s", "%s"', request, request.history)
        if len(request.history) != 0:
            return True
        
        # ix = request.content.find('\n')
        # firstLine = request.content[:ix]
        # logger.debug('First line "%s"', firstLine)
        # return 'Please log in' in firstLine
        return 'Please log in' in request.content

    def visitURL(self, URL, recursionCall=False, extension='.html', timeout=5):
        """ RecursionCall is used to limit recursion to 1 step
         Extension is used for the cache for ease of debugging
        """
        content = self.browser_cache.visitURL(URL, extension)
        if content == None:
            logger.info('Visiting %s', URL)

            try:
                r = self.client.get(URL, timeout=timeout)
            except requests.ConnectionError:
                print('Could not connect to {0}'.format(URL))
                return ''
            except requests.ConnectionError as e:
                print('Could not connect to {0}. {1}'.format(URL, e))
                return ''
            except requests.Timeout as e:
                print('Connection to {0}, timed out. {1}'.format(URL, e))
                return ''
            except Exception as e:
                print('Uncaught exception for {}. {}'.format(URL, e))
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

    def getParser(self, project=None):
        return HTMLParser.getParser(self.section, browser=self, p=project)

    def parse(self, project=None):
        parser = self.getParser(project=project)

        taskPage = self.visit()
        if taskPage == '':
            return parser.project # empty project

        try:
            try:
                parser.getBadges()
            except AttributeError as e:  # Parser does not implement getBadges
                logging.debug('no badge for %s, %s', self.section, e)

            parser.parse(taskPage)            
        except Exception as e:
            logger.exception('Uncaught parse exception %s', e)

        return parser.project

    @property
    def name(self):
        ret = self.section
        if not(self.section.startswith('www.')):
            ret = 'www.' + ret
        return 'https://' + ret

class Browser_worldcommunitygrid(BrowserSuper):
    def __init__(self, browser_cache, CONFIG):
        BrowserSuper.__init__(self, browser_cache)
        self.CONFIG = CONFIG
        username = self.CONFIG.get('worldcommunitygrid.org', 'username')
        password = CONFIG.getpassword('worldcommunitygrid.org', 'username'),
        code = self.CONFIG.get('worldcommunitygrid.org', 'code')

        self.section = 'worldcommunitygrid.org'
        name = 'https://secure.worldcommunitygrid.org' # todo: override property in superclass?
        self.URL = name+'/api/members/{username}/results?code={code}&json=true'.format(username=username, code=code)
        self.URL = self.URL + '&limit=25&offset={offset}'
        self.statistics = name+'/verifyMember.do?name={username}&code={code}&xml=true'.format(username=username, code=code)
        # self.URL = self.name +\
        #            '/ms/viewBoincResults.do?filterDevice=0&filterStatus=-1&projectId=-1&pageNum={0}&sortBy=sentTime'

        self.loginInfo = {
            'settoken': 'on',
            'j_username': username,
            'j_password': password
            }
        self.loginPage = 'https://secure.worldcommunitygrid.org/j_security_check' # TODO: needed?

    def visitStatistics(self):
        page = self.visitURL(self.statistics, extension='.xml')
        return page

    def visit(self, page=1, **kwargs):
        # Visit task page
        URL = self.URL.format(offset=25*(page-1)) # page = 1 gives offest 0, page = 2 gives offset 25, ...
        
        if URL in self.visitedPages: return ''
        self.visitedPages.append(URL)

        return self.visitURL(URL, extension='.json', **kwargs)

        
class Browser(BrowserSuper):
    def __init__(self, section, browser_cache, CONFIG, show_names=1):
        self.section = section
        BrowserSuper.__init__(self, browser_cache)
        
        self.userid = CONFIG.get(section, 'userid')
        self.URL = 'https://{name}/results.php?userid={userid}'.format(
            name = section,
            userid=self.userid)
        self.URL += '&offset={0}&show_names=%d&state=0&appid=' % show_names

        self.loginInfo = {'email_addr': CONFIG.get(section, 'username'),
                          'mode': 'Log in',
                          'next_url': 'home.php',
                          'passwd': CONFIG.getpassword(section, 'username'),
                          'stay_logged_in': 'on', # used by mindmodeling and wuprop
                          'send_cookie': 'on'}    # used by rosetta and yoyo
        self.loginPage = 'https://{0}/login_action.php'.format(section)

    def visitHome(self):
        return self.visitURL('https://{0}/home.php'.format(self.section))

    def visit(self, offset=0, **kwargs):
        return BrowserSuper.visit(self, offset, **kwargs)

class Browser_yoyo(Browser):
    def __init__(self, browser_cache, CONFIG):
        Browser.__init__(self, section='www.rechenkraft.net/yoyo',
                         browser_cache=browser_cache, CONFIG=CONFIG)
        self.loginInfo['mode'] = 'Log in with email/password'
        self.loginInfo['next_url'] = '/yoyo/home.php'

def getProject(section, CONFIG, browser_cache):
    """Gets a single project object based on section"""
    # projects = list()
    # for section in CONFIG.sections():
    logger.debug('section %s', section)
    # Pick subclass
    if section == 'worldcommunitygrid.org':
        browser = Browser_worldcommunitygrid(browser_cache, CONFIG)
    elif section == 'www.rechenkraft.net/yoyo':
        browser = Browser_yoyo(browser_cache, CONFIG)
    elif section == 'configuration': # Not a boinc project
        return None
    else:                   # Lets try the generic
        browser = Browser(section=section, 
                          browser_cache=browser_cache, 
                          CONFIG=CONFIG)
    return browser.parse()


def getProjects_wuprop(CONFIG, browser_cache):
    """Returns dictionary of wuprop projects, key is user_friendly_name"""
    section = 'wuprop.boinc-af.org'
    if section not in CONFIG.projects():
        return {}

    browser =  Browser(section=section, 
                       browser_cache=browser_cache, 
                       CONFIG=CONFIG)
    parser = HTMLParser.getParser(section, browser=browser)
    html = browser.visitHome()
    if html == '':
        return {}

    try:
        return parser.projectTable(html)
    except Exception as e:
        logger.exception('Uncaught parse exception %s', e)
        return {}

    
def getProjectsDict(CONFIG, browser_cache):
    """Async version og getProjet, returns a dictionary of projects where key is url"""
    sections = CONFIG.projects()
    projects_list = async.Pool(getProject, *sections, 
                               CONFIG=CONFIG, browser_cache=browser_cache)
    projects = dict()
    for p in projects_list.ret:
        projects[p.url] = p    
    return projects

if __name__ == '__main__':
    from loggerSetup import loggerSetup
    loggerSetup(logging.DEBUG)
    
    import config
    
    parser = argparse.ArgumentParser(description='Web portion of pyBoincPlotter')
    parser.add_argument('section', default='all', help='Section name to visit, see config file for details.')
    args = parser.parse_args()
    
    CONFIG, CACHE_DIR, _ = config.set_globals()
    browser_cache = Browser_file(CACHE_DIR)
    
    if args.section == 'all':
        projects = getProjectsDict(CONFIG, browser_cache)
    else:        
        valid_sections = CONFIG.projects()
        section = args.section
        if not(section in valid_sections):
            print 'Invalid section name, either add to config file or use one of: "%s"' % valid_sections
            exit(1)

        if section == 'wuprop.boinc-af.org':
            wuprop_projects = getProjects_wuprop(CONFIG, browser_cache)
            print 'wu-prop:', wuprop_projects
            
        p = getProject(section, CONFIG=CONFIG, browser_cache=browser_cache)
        projects = dict(section=p)

    pretty_print(projects, show_empty=True)
