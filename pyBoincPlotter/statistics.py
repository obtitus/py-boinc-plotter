
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
import datetime
import collections
import logging
logger = logging.getLogger('boinc.statistics')
# non standard
from bs4 import BeautifulSoup
# this project
from loggerSetup import loggerSetup
import util

class StatisticsList(list):
    """A really wierd hack"""
    def __getattr__(self, name):
        for item in self:
            try:
                return getattr(item, name)
            except AttributeError:
                pass
        raise AttributeError("'StatisticsList' object has no attribute '%s'" % name)

    def __str__(self):
        ret = [str(item) for item in self]
        return " ".join(ret)

class ProjectStatistics(object):
    def __init__(self, user_total_credit, user_expavg_credit,
                 host_total_credit, host_expavg_credit):
        self.user = (float(user_total_credit), float(user_expavg_credit))
        self.host = (float(host_total_credit), float(host_expavg_credit))        
    
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
        return ProjectStatistics.createFromSoup(soup)

    @staticmethod
    def createFromSoup(soup):
        return ProjectStatistics(soup.user_total_credit.text,
                          soup.user_expavg_credit.text,
                          soup.host_total_credit.text,
                          soup.host_expavg_credit.text)

    def __str__(self):
        length_user = len(util.fmtNumber(self.user[0], '.0f')) # user will always be longer than host
        length_host = len(util.fmtNumber(self.host[0], '.0f')) # user will always be longer than host
        
        def line(name, ix):
            if self.user[ix] != 0:
                per = self.host[ix]/self.user[ix]*100
            else:
                per = 0
            return '{} user: {:>{u}}, host: {:>{h}}, {:>3.0f}%'.format(name,
                                                                       util.fmtNumber(self.user[ix], '.0f'),
                                                                       util.fmtNumber(self.host[ix], '.0f'),
                                                                       per,
                                                                       u = length_user,
                                                                       h = length_host)
        return "{}\n{}".format(line('Total credit, ', 0), 
                               line('Avg credit,   ', 1))

class ProjectStatistics_worldcommunitygrid(object):
    def __init__(self, lastResult, runtime, runtimeRank, runtimePerDay, points, 
                 pointsRank, pointsPerDay, results, resultsRank, resultsPerDay):
        self.runtime       = datetime.timedelta(seconds=float(runtime))
        self.runtimeRank   = int(runtimeRank)
        self.runtimePerDay = datetime.timedelta(seconds=float(runtimePerDay))
        self.points        = int(points)
        self.pointsRank    = int(pointsRank)
        self.pointsPerDay  = float(pointsPerDay)
        self.results       = int(results)
        self.resultsRank   = int(resultsRank)
        self.resultsPerDay = float(resultsPerDay)
        self.lastResult    = lastResult

    def __str__(self):
        s = 'Worldcommunitygrid.org\nLast result returned: {0}\n'.format(self.lastResult)
        run = 'Run time {0:>20} total (#{2}), {1:>10} per day'.format(self.runtime, 
                                                                      self.runtimePerDay, 
                                                                      util.fmtNumber(self.runtimeRank))
        p   = 'Points   {0:>20} total (#{2}), {1:>10} per day'.format(util.fmtNumber(self.points), 
                                                                      util.fmtNumber(self.pointsPerDay, '.1f'), 
                                                                      util.fmtNumber(self.pointsRank))
        res = 'Results  {0:>20} total (#{2}), {1:>10} per day'.format(util.fmtNumber(self.results), 
                                                                      util.fmtNumber(self.resultsPerDay, '.1f'), 
                                                                      util.fmtNumber(self.resultsRank))
        s += '{:>10}\n{:>10}\n{:>10}'.format(run, p, res)
        return s

class ApplicationStatistics(object):
    def __init__(self, credit, results):
        self.credit  = float(credit)
        self.results = float(results)
    
    @property
    def credit_str(self):
        return util.fmtNumber(self.credit)

    @property
    def results_str(self):
        return util.fmtNumber(self.results)

    def __str__(self):
        return ("{s.results_str} results returned, "
                "{s.credit_str} credit.").format(s=self)

class ApplicationStatistics_worldcommunitygrid(ApplicationStatistics):
    def __init__(self, runtime, credit, results):
        ApplicationStatistics.__init__(self, credit, results)
        self.runtime = util.strToTimedelta(runtime)
    
    @property
    def runtime_str(self):
        return util.timedeltaToStr(self.runtime)

    def __str__(self):
        sup = ApplicationStatistics.__str__(self)
        return "{sup}, runtime of {s.runtime_str}.".format(sup=sup[:-1],
                                                           s=self)

class ApplicationStatistics_wuprop(object):
    def __init__(self, runtime, pending):
        def toSec(x):
            x = x.replace(',', '')
            sec = float(x)*60*60
            return datetime.timedelta(seconds=sec)
        self.wuRuntime = toSec(runtime)
        self.wuPending = toSec(pending)
    
    @property
    def wuRuntime_str(self):
        return util.timedeltaToStr(self.wuRuntime)

    @property
    def wuPending_str(self):
        return util.timedeltaToStr(self.wuPending)

    def __str__(self):
        ret = "WuProp runtime {}".format(self.wuRuntime_str)
        if self.wuPending != datetime.timedelta(0):
            ret += " (+{})".format(self.wuPending_str)
        return ret
    
class ProjectStatistics_primegrid(dict):
    def __str__(self):
        out = dict(self)
        ret = []
        def append(key, fmt='{}'):
            try:
                value = out[key]
                ret.append(fmt.format(value))
                del out[key]
            except KeyError:
                pass

        append('name')
        # Only one of these will actually do something:
        append('Completed tests', '{} results returned')
        append('Completed tasks', '{} results returned')
        append('Credit', '{} credits')
        
        # Remaining:
        for key in sorted(out):
            try:
                if out[key] == '':
                    continue
                elif float(out[key]) == 0:
                    continue
            except:
                pass

            ret.append("{} {}".format(key, self[key]))
        return ", ".join(ret) + '\n'
