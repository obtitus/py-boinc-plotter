# Standard import
import re
import datetime
import logging
logger = logging.getLogger('boinc.application')

# non standard
from bs4 import BeautifulSoup
# This project
import task

class Application(object):
    def __init__(self, name='', badge='', statistics=''):
        self.setName_shortLong(name)                # Hopefully on the form Say No to Schistosoma (sn2s)
        self.tasks = list()
        self.badge = badge
        self.statistics = statistics
    
    @property
    def credit(self):
        try:
            return self.statistics.credit
        except:
            try:
                return self.badge.credit
            except:
                return 0

    @property
    def runtime(self):
        try:
            return self.statistics.runtime
        except:
            try:
                return self.badge.runtime
            except:
                return 0

    def setNameFromXML(self, xml):
        """
        Expects the application block:
        <app>
        ...
        </app>
        from the boinc rpc
        """        
        soup = BeautifulSoup(xml, "xml")
        self.setNameFromSoup(soup)

    def setNameFromSoup(self, soup):
        self.name_short = soup.find('name').text   # Vops: soup.name is 'reserved' so need to use find('name')
        user_friendly_name = soup.find('user_friendly_name').text
        #self.setName_shortLong(user_friendly_name)
        self.name_long  = user_friendly_name

    def appendTaskFromXML(self, xml):
        t = task.Task_local.createFromXML(xml)
        self.tasks.append(t)
        return t
    
    def appendStatistics(self, statistics):
        # TODO: consider keeping a reference to the object
        #self.statistics += str(statistics)
        assert self.statistics == ''
        self.statistics = statistics
        
    # Name
    """Name should be on the form <long> (<short>), do a regexp when the name is set.
    name_long returns <long> and name_short returns <short>"""
    @property
    def name(self):
        return "{} ({})".format(self.name_long, self.name_short)

    def setName_shortLong(self, name):
        """
        Sets self.name_long and self.name_short based on the following pattern
        <long> (<short>)
        """
        try:
            reg = re.findall('([^(]+)\((\w+)\)', name)
        except TypeError as e:
            logging.exception('Expected string, got type = %s, "%s"', type(name), name)
            reg = []

        if reg != []:
            reg = reduce(lambda x,y: x+y, reg) # flatten list
            name_long = "".join(reg[:-1]).strip()
            name_short = reg[-1].strip()
        else:
            name_long = name
            name_short = ''
        
        self.setName_long(name_long)
        self.name_short = name_short

    def setName_long(self, name_long=None):
        """
        Removes the version part of the application long name (if any)
        """
        if name_long is None: name_long = self.name_long
        
        reg = re.search('(v\d+.\d+)', name_long)
        if reg:
            s = reg.start()
            e = reg.end()
            self.version = reg.group()
            name_long = name_long[:s] + name_long[e:]
        else:
            name_long = name_long
        self.name_long = name_long.strip()

    def __str__(self):
        ret = ["= {} = {} {}".format(self.name, self.statistics, 
                                     self.badge)]
        for t in self.tasks:
            ret.append(str(t))
        return "\n".join(ret)

    def __len__(self):
        """
        Number of tasks
        """
        return len(self.tasks)

    def pendingTime(self):
        """Returns total seconds for
        pending,
        started
        and tasks waiting for validation.
        """
        pending = 0
        running = 0
        validation = 0
        for task in self.tasks:
            try:
                (p, r, v) = task.pendingTime()
                pending    += p
                running    += r
                validation += v 
            except AttributeError:
                pass

        return pending, running, validation


def mergeApplications(local_app, web_app):
    """Tries to merge local and web information by adding information from local to the web application"""
    local_tasks = list(local_app.tasks)
    web_tasks = web_app.tasks
    ix = 0
    while ix < len(local_tasks):
        logger.debug('looking for %s', local_tasks[ix].name)
        #if local_task[ix] in web_app.tasks:
        for jx in range(len(web_tasks)):
            logger.debug('is it %s', web_tasks[jx].name)
            if web_tasks[jx].name.startswith(local_tasks[ix].name):
                logger.debug('Found it, replacing %s', web_tasks[ix])
                web_tasks[jx] = local_tasks[ix] # Local has more info then web
                del local_tasks[ix]
                break
        else:
            ix += 1

    for remaining_task in local_tasks:
        web_app.tasks.append(remaining_task)
