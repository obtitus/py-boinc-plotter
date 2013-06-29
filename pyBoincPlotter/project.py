# Standard python
import re
import logging
logger = logging.getLogger('boinc.project')
# non standard
from bs4 import BeautifulSoup
# This project:
from application import Application
from task import Task_local
from statistics import Statistics

class Project(object):
    def __init__(self, url, user=None, statistics=None, settings=None):
        self.name = url
        self.user = user
        self.applications = dict()
        self.statistics = statistics
        self.settings = settings

        self._appNames = dict() # key is name and value is application name

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
        # For now, settings is just a string
        settings = 'Resource share {:.3g}%'.format(float(soup.resource_share.text))
        if soup.dont_request_more_work is not None:
            settings += ", Don't request more work"
        # Get the statistics
        s = Statistics.createFromSoup(soup)
        return Project(soup.master_url.text, statistics=s, settings=settings)

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
        logger.debug('result %s', t)

        try:
            app_name = self._appNames[t.name]
        except KeyError:
            raise KeyError('Unknown app_name for task %s, known names %s', t.name, self._appNames)

        #logger.debug('trying to find app_name %s', app_name)
        for key, app in self.applications.items():
            if app.name_short == app_name:
                app.tasks.append(t)
                break
        else:
            raise KeyError('Could not find app_name %s in list of applications', app_name)

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
        self.name_short = name.replace('https://', '')
        self.name_short = self.name_short.replace('http://', '')
        self.name_short = self.name_short.replace('www.', '')
        self.name_short = self.name_short.replace('.org', '')
        if self.name_short[-1] == '/':
            self.name_short = self.name_short[:-1]

    def __str__(self):
        endl = '\n'
        ret = ["== {} ==".format(self.name_short.capitalize())]
        for prop in [self.settings, self.statistics]:
            if prop != None:
                ret.append(str(prop))

        for key in self.applications:
            ret.append(str(self.applications[key]))

        return "\n".join(ret)
