#!/usr/bin/env python
# This file is part of the py-boinc-plotter, which provides parsing and plotting of boinc statistics and badge information.
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
# 
# END LICENCE
"""
Deals with the 'public' xml stat
"""
import re
import datetime
import xml.etree.ElementTree

import logging
logger = logging.getLogger('boinc.statistics')

from bs4 import BeautifulSoup

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
    def __init__(self, short='', name='', runtime=None, points=None, results=None, badge='', badgeURL='', pending=None, wuRuntime=None, wuPending=None):
        self.short = short
        self.name = name
        self.runtime = strToTimedelta(runtime)
        self.pending = strToTimedelta(pending)
            
        if points != None:
            self.points = float(points)
            #self.points = fmtNumber(self.points)
        else:
            self.points = points
            
        self.results = results
        self.badge = badge
        self.badgeURL = badgeURL
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
            ret += "{points:>6} points, ".format(points=fmtNumber(self.points))
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
        s = 'Worldcommunitygrid.org\nLast result returned: {0}\n'.format(self.lastResult)
        run = 'Run time {0:>20} total, {1:>10} per day (#{2})'.format(self.runtime, self.runtimePerDay, fmtNumber(self.runtimeRank))
        p   = 'Points   {0:>20} total, {1:>10.3g} per day (#{2})'.format(fmtNumber(self.points), self.pointsPerDay, fmtNumber(self.pointsRank))
        res = 'Results  {0:>20} total, {1:>10.3g} per day (#{2})'.format(fmtNumber(self.results), self.resultsPerDay, fmtNumber(self.resultsRank))
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
        projects[name].badge = t
        projects[name].badgeURL = badgeURL
#         for key in projects:
#             if projects[key].name == name:
#                 projects[key].badge += badge
                
    return statistics, projects

class HTMLParser_boinchome():
    def __init__(self):
#         HTMLParser.__init__(self)
#         self.inTable = False
#         self.inTr = False
#         self.inHeading = False
#         self.inFieldname = False
#         self.inReportTable = False
#         self.inBadge = False

        # Public info
        self.projects = dict()
        self.badge = ''

    def feed(self, page, wuprop=False):
        self.soup = BeautifulSoup(page)
        self.getYoYoTable()
        if wuprop:
            self.getWuPropTable()

    def getYoYoTable(self):
        # Extracts projects table from www.rechenkraft.net/yoyo
        # Hopefully does nothing if the page is not www.rechenkraft.net/yoyo.
        # In case other projects implement a similar table a test is not made
        for t in self.soup.find_all('table'):
            badgeTable = t.table            # The table within a table
            if badgeTable != None:
                for row in badgeTable.find_all('tr'):
                    data = row.find_all('td')
                    if len(data) == 4:
                        name = data[0].text
                        totalCredits = data[1].text.replace(',', '') # thousand seperator
                        workunits = data[2].text
                        if re.match('\d+ \w\w\w \d\d\d\d', data[3].text): # Hack to avoid the "Projects in which you are participating" table.
                            continue
                        
                        badge = ''
                        badgeURL = None
                        if data[3].a:
                            badge = data[3].a.img['alt']
                            badgeURL = data[3].a.img['src']

                        self.projects[name] = Project(name=name, points=totalCredits, results=workunits, badge=badge, badgeURL=badgeURL)

    def getWuPropTable(self):
        # Extracts projects table from wuprop.boinc-af.org/home.php
        t = self.soup.find_all('table')
        for row in t[-1].find_all('tr'):
            data = row.find_all('td')
            if len(data) == 4:
                projects = data[0].text
                application = data[1].text
                runningTime = float(data[2].text)*60*60
                pending = float(data[3].text)*60*60
                self.projects[application] = Project(short=projects, name=application, wuRuntime=runningTime, wuPending=pending)
        
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

    b = browser.Browser('www.rechenkraft.net/yoyo')
    page = b.visitHome()
    parser = HTMLParser_boinchome()
    parser.feed(page)
    for k in parser.projects:
        print k, parser.projects[k]

#     b = browser.Browser('boinc.bakerlab.org')
#     page = b.visitHome()
#     parser = HTMLParser_boinchome()
#     parser.feed(page)
#     for k in parser.projects:
#         print k, parser.projects[k]
