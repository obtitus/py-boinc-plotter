# Standard import
import datetime
import logging
logger = logging.getLogger('boinc.statistics')
# non standard
from bs4 import BeautifulSoup
# this project
from loggerSetup import loggerSetup
from util import fmtNumber

class Statistics(object):
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
        return Statistics.createFromSoup(soup)
    @staticmethod
    def createFromSoup(soup):
        return Statistics(soup.user_total_credit.text,
                          soup.user_expavg_credit.text,
                          soup.host_total_credit.text,
                          soup.host_expavg_credit.text)

    def __str__(self):
        length_user = len(fmtNumber(self.user[0], '.0f')) # user will always be longer than host
        length_host = len(fmtNumber(self.host[0], '.0f')) # user will always be longer than host
        
        def line(name, ix):
            return '{} user: {:>{u}}, host: {:>{h}}, {:>3.0f}%'.format(name,
                                                                     fmtNumber(self.user[ix], '.0f'),
                                                                     fmtNumber(self.host[ix], '.0f'),
                                                                     self.host[ix]/self.user[ix]*100,
                                                                     u = length_user,
                                                                     h = length_host)
        return "{}\n{}".format(line('Total credit, ', 0), 
                               line('Avg credit,   ', 1))

class Statistics_worldcommunitygrid(object):
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
        run = 'Run time {0:>20} total, {1:>10} per day (#{2})'.format(self.runtime, 
                                                                      self.runtimePerDay, 
                                                                      fmtNumber(self.runtimeRank))
        p   = 'Points   {0:>20} total, {1:>10.3g} per day (#{2})'.format(fmtNumber(self.points), 
                                                                         self.pointsPerDay, 
                                                                         fmtNumber(self.pointsRank))
        res = 'Results  {0:>20} total, {1:>10.3g} per day (#{2})'.format(fmtNumber(self.results), 
                                                                         self.resultsPerDay, 
                                                                         fmtNumber(self.resultsRank))
        s += '{:>10}\n{:>10}\n{:>10}'.format(run, p, res)
        return s
