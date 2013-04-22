"""
Deals with the 'public' xml stat
"""

import datetime
import xml.etree.ElementTree
from HTMLParser import HTMLParser

import logging
logger = logging.getLogger('boinc.statistics')

from loggerSetup import loggerSetup
import config


def fmtNumber(x):
    # Hack    
    return "{:,}".format(x).replace(',', ' ')

def timedeltaToStr(timedelta):
    # Hack
    timedelta = str(timedelta)
    ix = timedelta.find('.')
    if ix != -1:
        timedelta = timedelta[:ix]
    return timedelta
def strToTimedelta(string):
    if string != None:
        return datetime.timedelta(seconds=float(string))
    else:
        return None
    
class Project(object):
    def __init__(self, short, name, runtime=None, points=None, results=None, badge='', pending=None, wuRuntime=None, wuPending=None):
        self.short = short
        self.name = name
        self.runtime = strToTimedelta(runtime)
        self.pending = strToTimedelta(pending)
            
        if points != None:
            self.points = int(points)
            self.points = fmtNumber(self.points)
        else:
            self.points = points
            
        self.results = results
        self.badge = badge
        self.badgeURL = list()
        self.__repr__ = self.__str__

        self.wuRuntime = strToTimedelta(wuRuntime)
        self.wuPending = strToTimedelta(wuPending)
            
    def __str__(self):
        #ret = "{self.name:<40} ({self.short:<5}), {self.results:>3} results returned, {self.points:>6} points generated with a runtime of {self.runtime:>17} {self.badge}".format(self=self)
        ret = ''
        if self.wuRuntime != None:
            ret += 'Wu runtime of {runtime}, '.format(runtime=timedeltaToStr(self.wuRuntime))
        if self.wuPending != None:
            ret += 'pending {pending}, '.format(pending=timedeltaToStr(self.wuPending))
        if self.results != None:
            ret += "{self.results:>3} results returned, ".format(self=self)
        if self.points != None:
            ret += "{self.points:>6} points, ".format(self=self)
        if self.runtime != None:
            ret += "runtime of {runtime:>17}. ".format(runtime=timedeltaToStr(self.runtime))
        if self.pending != None:
            ret += "pending {pending}. ".format(pending=timedeltaToStr(self.pending))
        ret += self.badge
        return ret.strip()

class Statistics_worldcommunitygrid(object):
    def __init__(self, lastResult, runtime, runtimeRank, runtimePerDay, points, pointsRank, pointsPerDay, results, resultsRank, resultsPerDay):
        self.runtime = datetime.timedelta(seconds=float(runtime))
        self.runtimeRank = int(runtimeRank)
        self.runtimePerDay = datetime.timedelta(seconds=float(runtimePerDay))
        self.points = int(points)
        self.pointsRank = int(pointsRank)
        self.pointsPerDay = float(pointsPerDay)
        self.results = int(results)
        self.resultsRank = int(resultsRank)
        self.resultsPerDay = float(resultsPerDay)
        self.lastResult = lastResult

    def __str__(self):
        s = 'Worldcommunitygrid.org\nLast result returned: {}\n'.format(self.lastResult)
        run = 'Run time {:>20} total, {:>10} per day (#{})'.format(self.runtime, self.runtimePerDay, fmtNumber(self.runtimeRank))
        p   = 'Points   {:>20} total, {:>10.3g} per day (#{})'.format(fmtNumber(self.points), self.pointsPerDay, fmtNumber(self.pointsRank))
        res = 'Results  {:>20} total, {:>10.3g} per day (#{})'.format(fmtNumber(self.results), self.resultsPerDay, fmtNumber(self.resultsRank))
        s += '{:>10}\n{:>10}\n{:>10}'.format(run, p, res)
        return s

def parse(page):
    tree = xml.etree.ElementTree.fromstring(page)

    e = tree.find('Error')
    if e:
        print e.text
        return None, None

    try:
        member = tree.iter('MemberStat').next()
    except StopIteration:
        print 'Something is wrong with xml statisics, correct username and code?'
        return None, None
    lastResult = member.find('LastResult').text
    lastResult = lastResult.replace('T', ' ')

    stat = list()
    for s in ['RunTime', 'RunTimeRank', 'RunTimePerDay',
              'Points', 'PointsRank', 'PointsPerDay',
              'Results', 'ResultsRank', 'ResultsPerDay']:
        i = member.iter(s).next()
        stat.append(i.text)
    statistics = Statistics_worldcommunitygrid(lastResult, *stat)
    
    projects = dict()
    for project in tree.iter('Project'):
        short = project.find('ProjectShortName').text
        name = project.find('ProjectName').text
        runtime = project.find('RunTime').text
        points = project.find('Points').text
        results = project.find('Results').text
        projects[name] = Project(short, name, runtime, points, results)

    for badge in tree.iter('Badge'):
        name = badge.find('ProjectName').text
        badgeURL = badge.iter('Url').next().text        
        t = badge.iter('Description').next().text
        projects[name].badge += t
        projects[name].badgeURL.append(badgeURL)
#         for key in projects:
#             if projects[key].name == name:
#                 projects[key].badge += badge
                
    return statistics, projects

class HTMLParser_boinchome(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.inTable = False
        self.inTr = False
        self.inHeading = False
        self.inFieldname = False
        self.inReportTable = False
        self.inBadge = False

        # Public info
        self.projects = dict()
        self.currentProject = list()
        self.badge = ''
        
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.inTable = True
        if tag == 'tr' and self.inTable:
            self.inTr = True
        if tag == 'td' and self.inTable:
            try:
                if attrs[0][1] == 'heading':
                    self.inHeading = True
                if attrs[1][1] == 'fieldname':
                    self.inFieldname = True
            except IndexError: pass
        
        
    def handle_endtag(self, tag):
        if tag == 'table':
            self.inTable = False
            self.inReportTable = False
        if tag == 'tr':
            self.inTr = False
            self.inBadge = False            
            
            if len(self.currentProject) == 4 and self.currentProject[0] != 'Project': # correct length and not heading
                name = self.currentProject[1]
                
                self.projects[name] = Project(short=self.currentProject[0],
                                              name=name,
                                              wuRuntime=float(self.currentProject[2])*60*60, # hours
                                              wuPending=float(self.currentProject[3])*60*60)
            self.currentProject = list() # reset
        if tag == 'td':
            self.inHeading = False
            self.inFieldname = False

    def handle_data(self, data):
        if self.inHeading:
            if data == 'Reported data':
                self.inReportTable = True
        if self.inBadge:
            if data.strip() != '':
                self.badge += data      # TODO does this work?
        if self.inFieldname:
            if data == 'Badge':
                self.inBadge = True
        if self.inReportTable:
            if data.strip() != '':
                self.currentProject.append(data)
        
if __name__ == "__main__":    
    loggerSetup(logging.INFO)

    import browser
    ### Make global variables ###
    config.main()
    browser.main()
    
    b = browser.Browser('wuprop.boinc-af.org')
    page = b.visitHome()
    parser = HTMLParser_boinchome()
    parser.feed(page)
    print parser.projects

    
#     page = getPage()
#     if page == None: exit(1)
#     totalStats, projects = parse(page)
#     print totalStats
#     for key in projects:
#         print projects[key]
