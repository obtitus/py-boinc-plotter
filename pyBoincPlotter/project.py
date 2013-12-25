
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
# Standard python
import re
import difflib
import logging
logger = logging.getLogger('boinc.project')
# non standard
from bs4 import BeautifulSoup
# This project:
from application import Application, mergeApplications
from task import Task_local, adjustColumnSpacing
from statistics import ProjectStatistics, StatisticsList
from settings import Settings

class Project(object):
    def __init__(self, url=None, name=None, 
                 user=None, statistics=None, settings=None):
        self.name = name
        if name == None:
            self.setName(url)
        self.setUrl(url)

        self.user = user
        self.applications = dict()
        self.statistics = statistics
        self.settings = settings

        self._appNames = dict() # key is task name and value is application name
        self._badges = list()
        self.show_empty = False

    # 
    # XML related
    # 
    @staticmethod
    def createFromXML(xml):
        """
        Expects the project block:
        <project>
        ...
        </project>
        from the boinc rpc
        """        
        soup = BeautifulSoup(xml, "xml")
        settings = Settings.createFromSoup(soup)
        # Get the statistics
        s = ProjectStatistics.createFromSoup(soup)
        url = soup.master_url.text
        name = soup.project_name.text
        return Project(url=url, name=name,
                       statistics=s, settings=settings)

    def appendApplicationFromXML(self, xml):
        a = Application()
        a.setNameFromXML(xml)
        self.applications[a.name_long] = a
        return a
    
    def appendWorkunitFromXML(self, xml):
        # Currently, the only thing of interest is the mapping between name and app_name
        soup = BeautifulSoup(xml)
        name = soup.find('name').text
        app_name = soup.find('app_name').text
        self._appNames[name] = app_name
        return 'name %s, app_name %s' % (name, app_name)
    
    def appendResultFromXML(self, xml):
        t = Task_local.createFromXML(xml)

        try:
            app_name = self._appNames[t.name]
        except KeyError:
            raise KeyError('Unknown app_name for task %s, known names %s' % (t.name, self._appNames))

        #logger.debug('trying to find app_name %s', app_name)
        for key, app in self.applications.items():
            if app.name_short == app_name:
                app.tasks.append(t)
                break
        else:
            raise KeyError('Could not find app_name %s in list of applications' % app_name)

        return t

    # 
    # HTML related
    # 
    def appendApplication(self, name, is_long=False):
        app = Application(name=name, is_long=is_long)
        name_long = app.name_long
        if not(name_long in self.applications):
            self.applications[name_long] = app

        return self.applications[name_long]

    def appendBadge(self, app_name='', badge=''):
        # Normally badges are associated with an application, but numbersfields and wuprop associates with project instead.
        if app_name != '':
            app = self.appendApplication(app_name)
            logger.debug('Appending badge %s, to %s', badge, app_name)
            app.badge = badge
            return app
        else:
            self._badges.append((self, badge))

    @property
    def badges(self):
        ret = list()
        for key, app in sorted(self.applications.items()):
            b = app.badge
            if b != '':
                ret.append((app, b))
        ret.extend(self._badges)
        return ret
        
    def appendStatistics(self, statistics):
        if statistics is None:
            return

        logger.debug('Appending project statistics "%s" to "%s"', 
                     statistics, self.statistics)
        if self.statistics is None:
            self.statistics = StatisticsList([statistics])
        elif isinstance(statistics, list):
            self.statistics.extend(statistics)
        else:
            self.statistics.append(statistics)
        
    def setName(self, name):
        if name == None: 
            self.name = name
            return

        self.name = name.replace('https://', '')
        self.name = self.name.replace('http://', '')
        self.name = self.name.replace('www.', '')
        self.name = self.name.replace('.org', '')
        if self.name[-1] == '/':
            self.name = self.name[:-1]
        self.name = self.name.replace('/', '_')
        self.name = self.name#.capitalize()

    def setUrl(self, url):
        if url is None:
            self.url = url
            return

        if url.endswith('/'):
            self.url = url[:-1]
        else:
            self.url = url

        http = 'http://'
        ix = self.url.find(http)
        if ix != -1:
            name = self.url[ix+len(http):]
            if not(name.startswith('www.')):
                name = 'www.' + name
                self.url = http + name

    def __str__(self):
        ret = ["== {} ==".format(self.name.title())]
        for prop in [self.settings, self.statistics]:
            if prop != None:
                ret.append(str(prop))

        for _, badge in self._badges:
            ret.append(str(badge))

        for key in sorted(self.applications):
            if len(self.applications[key]) != 0 or self.show_empty:
                ret.append(str(self.applications[key]))

        return "\n".join(ret)

    def __len__(self):
        """
        Number of tasks
        """
        n = 0
        for key in self.applications:
            n += len(self.applications[key])
        return n

    def tasks(self):
        """ Syntax sugar for generator for each task contained by project
        """
        for key in sorted(self.applications):
            for task in self.applications[key].tasks:
                yield task

class Project_fileTransfers(Project):
    def __init__(self, tasks):
        Project.__init__(self, name='File Transfers')
        a = Application(tasks=tasks)
        self.applications[''] = a

def merge(local_projects, 
          web_projects):
    """Tries to merge local and web information by adding information from local to the web dictionary"""
    local_projects = dict(local_projects)
    mergeDicts(local_projects, web_projects, mergeProject, 'url')

def mergeProject(local_project, web_project):
    local_apps = dict(local_project.applications)
    web_apps = web_project.applications
    mergeDicts(local_apps, web_apps, mergeApplications, 'name_long')

    web_project.appendStatistics(local_project.statistics)
    logger.debug('web_project.name "%s", local_project.name "%s"', 
                 web_project.name, local_project.name)
    web_project.name = local_project.name
    logger.debug('web_project.settings "%s", local_project.settings "%s"', 
                 web_project.settings, local_project.settings)
    if local_project.settings is not None:
        web_project.settings = local_project.settings

    return True
def mergeWuprop(wuprop_projects,
                local_projects):
    """Tries to merge the wuprop project dict (which is sorted by user_friendly_name)
    with the normal local_projects which are sorted by url. Works inplace on local_projects"""
    wuprop_projects = dict(wuprop_projects)
    for key in wuprop_projects.keys():
        wuprop_project = wuprop_projects[key]
        # find:
        for local_project in local_projects.values():
            if local_project.name == wuprop_project.name:
                mergeProject(wuprop_project,
                             local_project)
                del wuprop_projects[key]
                break
    
    for remaining in wuprop_projects:
        logger.info(('Problem merging wuprop project "%s", '
                     'this might be caused by this project not being '
                     'present locally'), remaining)
        local_projects[remaining] = wuprop_projects[remaining] # This is really messy, since remaining isn't a url

def mergeDicts(local_dict, web_dict, merge, name):
    """Helper function for above merge rutines"""
    logging.debug('merging with %s, ("%s", "%s")', merge, 
                  local_dict, web_dict)
    for key in local_dict.keys():
        if key in web_dict:
            if merge(local_dict[key],
                     web_dict[key]):
                del local_dict[key]

    def fuzzyMatch(name1, name2):
        if name1 is None or name2 is None: return False

        if name1.startswith(name2):
            return True
        if name2.startswith(name1):
            return True
        # This last one catches the following condition:
        # 'PPS (Sieve)' == 'PPS Sieve'
        name1 = name1.replace('(', '').replace(')', '')
        name2 = name2.replace('(', '').replace(')', '')
        return name1 == name2

    for remaining_key, remaining in local_dict.items():
        for web in web_dict.values():
            if fuzzyMatch(getattr(remaining, name),
                          getattr(web, name)):
                logger.debug('fuzzy match \n"%s", \n"%s"', 
                             remaining.name, web.name)
                if merge(remaining, web):
                    del local_dict[remaining_key]
                    break

    web_objects = web_dict.values()
    web_names   = [getattr(web, name) for web in web_objects]
    for remaining_key, remaining in local_dict.items():
        try:
            match = difflib.get_close_matches(getattr(remaining, name), web_names, n=1, cutoff=0.8)
            ix = web_names.index(match[0])
            logger.debug('difflib match \n"%s", \n"%s"', 
                         remaining.name, web_objects[ix].name)
            if merge(remaining, web_objects[ix]):
                del local_dict[remaining_key]
                #break
            else:
                raise IndexError()
        except (IndexError, TypeError):
            logger.warning('merge with %s failed, remaining local %s, web keys, %s', merge, remaining_key, web_dict.keys())
            web_dict[remaining_key] = local_dict[remaining_key]
            del local_dict[remaining_key]
    
    assert len(local_dict) == 0, 'Vops, not all projects merged %s' % local_dict
    
def pretty_print(projects, show_empty=False, show_checkpoint=False):
    for p in projects.values():
        for app in p.applications:
            tasks = p.applications[app].tasks
            adjustColumnSpacing(tasks)

    for key, p in sorted(projects.items()):
        p.show_empty = show_empty # hack
        if len(p) != 0 or show_empty:
            print str(p) + '\n'
