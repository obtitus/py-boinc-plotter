
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
# Standard import
import re
import datetime
import logging
logger = logging.getLogger('boinc.application')

# non standard
from bs4 import BeautifulSoup
# This project
import task
from statistics import StatisticsList, ApplicationStatistics_wuprop

class Application(object):
    def __init__(self, name='', badge='', statistics='', is_long=False):
        """use is_long = True when passed name is the long name (i.e. from wuprop)"""
        if not(is_long) and not(name is None):
            self.setName_shortLong(name)                # Hopefully on the form Say No to Schistosoma (sn2s)
        else:
            self.name_short = name
            self.name_long = name

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
                return datetime.timedelta(0)

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
        #self.statistics += str(statistics)
        logger.debug('Appending application statistics "%s" to "%s"', 
                     statistics, self.statistics)
        
        # TODO: shorten the code?
        if self.statistics == '':
            if isinstance(statistics, StatisticsList):
                self.statistics = statistics
            else:
                self.statistics = StatisticsList([statistics])
        else:
            if isinstance(statistics, StatisticsList):
                self.statistics.extend(statistics)
            else:
                self.statistics.append(statistics)
        
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
            name_long = name_long.replace('  ', ' ')
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

    def pendingTime(self, include_elapsedCPUtime=True):
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
                (p, r, v) = task.pendingTime(include_elapsedCPUtime=include_elapsedCPUtime)
                pending    += p
                running    += r
                validation += v 
            except AttributeError:
                pass

        return pending, running, validation


def mergeApplications(local_app, web_app):
    """Tries to merge local and web information by adding information from local to the web application"""
    logger.debug('mergeapplication %s %s', local_app.name, web_app.name)
    # This is a uggly hack which should be removed (currently needed to avoid merging too much).
    try:
        logger.debug('local_app.statistics[0] = %s, %s', local_app.statistics[0],
                     isinstance(local_app.statistics[0], ApplicationStatistics_wuprop))
        logger.debug('web_app.statistics[0] = %s, %s', web_app.statistics[0],
                     isinstance(web_app.statistics[0], ApplicationStatistics_wuprop))
        if isinstance(local_app.statistics[0], ApplicationStatistics_wuprop) and\
           isinstance(web_app.statistics[0], ApplicationStatistics_wuprop):
            logger.warning('Tried to merge "%s" and "%s", but both had wuprop stats', 
                           local_app.name, web_app.name)
            return False
    except (IndexError, TypeError):
        pass


    local_tasks = list(local_app.tasks)
    web_tasks = web_app.tasks
    ix = 0
    while ix < len(local_tasks):
        logger.debug('looking for %s', local_tasks[ix].name)
        #if local_task[ix] in web_app.tasks:
        for jx in range(len(web_tasks)):
            #logger.debug('is it %s', web_tasks[jx].name)
            if web_tasks[jx].name.startswith(local_tasks[ix].name):
                logger.debug('Found it, replacing %s', web_tasks[ix])
                web_tasks[jx] = local_tasks[ix] # Local has more info then web
                del local_tasks[ix]
                break
        else:
            ix += 1

    for remaining_task in local_tasks:
        web_app.tasks.append(remaining_task)

    if local_app.statistics != '':
        web_app.appendStatistics(local_app.statistics)
    
    if web_app.name_short == '':
        web_app.name_short = local_app.name_short

    return True
