# Standard python
import re
import logging
logger = logging.getLogger('boinc.project')
# non standard
from bs4 import BeautifulSoup
# This project:
from application import Application, mergeApplications
from task import Task_local, adjustColumnSpacing
from statistics import ProjectStatistics
from settings import Settings

class Project(object):
    def __init__(self, url, name=None, 
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
    def appendApplication(self, name):
        app = Application(name=name)
        name_long = app.name_long
        if not(name_long in self.applications):
            self.applications[name_long] = app

        return self.applications[name_long]

    def appendBadge(self, app_name, badge):
        app = self.appendApplication(app_name)
        logger.debug('Appending badge %s, to %s', badge, app_name)
        app.badge = badge
        return app

    @property
    def badge(self):
        ret = list()
        for key in sorted(self.applications):
            b = self.applications[key].badge
            if b != '':
                ret.append(b)
        return ret

    def appendStatistics(self, statistics):
        # TODO: consider keeping a reference to the object
        logger.debug('Appending statistics "%s"', statistics)
        if self.statistics is None:
            self.statistics = str(statistics)
        else:
            self.statistics += '\n' + str(statistics)
        
    def setName(self, name):
        self.name = name.replace('https://', '')
        self.name = self.name.replace('http://', '')
        self.name = self.name.replace('www.', '')
        self.name = self.name.replace('.org', '')
        if self.name[-1] == '/':
            self.name = self.name[:-1]
        self.name = self.name.replace('/', '_')
        self.name = self.name#.capitalize()

    def setUrl(self, url):
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
        endl = '\n'
        ret = ["== {} ==".format(self.name.title())]
        for prop in [self.settings, self.statistics]:
            if prop != None:
                ret.append(str(prop))

        for key in sorted(self.applications):
            if len(self.applications[key]) != 0:
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

def merge(local_projects, 
          web_projects):
    """Tries to merge local and web information by adding information from local to the web dictionary"""
    local_projects = dict(local_projects)
    mergeDicts(local_projects, web_projects, mergeProject, 'url')

def mergeProject(local_project, web_project):
    local_apps = dict(local_project.applications)
    web_apps = web_project.applications
    mergeDicts(local_apps, web_apps, mergeApplications, 'name_long')

def mergeDicts(local_dict, web_dict, merge, name):
    """Helper function for above merge rutines"""
    logging.debug('merging with %s, ("%s", "%s")', merge, 
                  local_dict, web_dict)
    for key in local_dict.keys():
        if key in web_dict:
            merge(local_dict[key],
                  web_dict[key])
            del local_dict[key]

    def fuzzyMatch(name1, name2):
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
                merge(remaining, web)
                break
        else:
            logger.warning('merge with %s, remaining local %s, web keys, %s', merge, remaining_key, web_dict.keys())
            web_dict[remaining_key] = local_dict[remaining_key]

    
def pretty_print(projects, show_empty=False):
    for p in projects.values():
        for app in p.applications:
            tasks = p.applications[app].tasks
            adjustColumnSpacing(tasks)

    for key, p in sorted(projects.items()):
        if len(p) != 0 or show_empty:
            print str(p) + '\n'
