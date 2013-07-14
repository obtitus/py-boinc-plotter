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
            return '{} user: {:>{u}}, host: {:>{h}}, {:>3.0f}%'.format(name,
                                                                       util.fmtNumber(self.user[ix], '.0f'),
                                                                       util.fmtNumber(self.host[ix], '.0f'),
                                                                       self.host[ix]/self.user[ix]*100,
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

class ApplicationStatistics_worldcommunitygrid(object):
    def __init__(self, runtime, points, results):
        self.runtime = util.strToTimedelta(runtime)
        self.points  = int(points)
        self.results = int(results)
    
    @property
    def runtime_str(self):
        return util.timedeltaToStr(self.runtime)

    @property
    def points_str(self):
        return util.fmtNumber(self.points)

    @property
    def results_str(self):
        return util.fmtNumber(self.results)

    def __str__(self):
        return ("{s.results_str} results returned, "
                "{s.points_str} points, "
                "runtime of {s.runtime_str}.").format(s=self)

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
        append('Credit', '{points}')
        
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
        return ", ".join(ret)
