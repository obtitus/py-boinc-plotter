# Standard python
import re
import collections
import logging
logger = logging.getLogger('boinc.project')
# non standard
from bs4 import BeautifulSoup
# This project:
from application import Application
from task import Task_local, adjustColumnSpacing
from statistics import Statistics

class Project(object):
    class Settings(collections.namedtuple('Settings', ['resource_share', 'dont_request_more_work', 'sched_priority'])):
        """
        Some of the project settings
        """
        @staticmethod
        def createFromSoup(soup):
            resource_share = float(soup.resource_share.text)
            dont_request_more_work = soup.dont_request_more_work != None
            sched_priority = float(soup.sched_priority.text)
            return Project.Settings(resource_share=resource_share,
                                    dont_request_more_work=dont_request_more_work,
                                    sched_priority=sched_priority)

        def __str__(self):
            ret = 'Resource share {:.3g}%, sched. priority {}'.format(self.resource_share,
                                                                      self.sched_priority)
            if self.dont_request_more_work:
                ret += ", Don't request more work"
            return ret
            
    def __init__(self, url, name=None, 
                 user=None, statistics=None, settings=None):
        self.name = name
        if name == None:
            self.setName(url)
        self.url = url

        self.user = user
        self.applications = dict()
        self.statistics = statistics
        self.settings = settings

        self._appNames = dict() # key is name and value is application name

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
        settings = Project.Settings.createFromSoup(soup)
        # Get the statistics
        s = Statistics.createFromSoup(soup)
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
    def appendApplication(self, name_long):
        if not(name_long in self.applications):
            a = Application(name=name_long)
            self.applications[name_long] = a

        return self.applications[name_long]

    def appendBadge(self, app_name, badge):
        app = self.appendApplication(name_long=app_name)
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

    def setName(self, name):
        self.name = name.replace('https://', '')
        self.name = self.name.replace('http://', '')
        self.name = self.name.replace('www.', '')
        self.name = self.name.replace('.org', '')
        if self.name[-1] == '/':
            self.name = self.name[:-1]
        self.name = self.name.replace('/', '_')
        self.name = self.name#.capitalize()
            
    def __str__(self):
        endl = '\n'
        ret = ["== {} ==".format(self.name)]
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

def pretty_print(projects, show_empty=False):
    for p in projects:
        for app in p.applications:
            tasks = p.applications[app].tasks
            adjustColumnSpacing(tasks)

    for p in projects:
        if len(p) != 0 or show_empty:
            print str(p) + '\n'
