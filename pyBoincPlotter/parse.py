
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
# Standard
import re
import logging
logger = logging.getLogger('boinc.browser')
import xml.etree.ElementTree
import json

# Non-standard python
from bs4 import BeautifulSoup
# This project
import task
import plot.badge as badge
import async
import statistics
import project

class HTMLParser(object):
    def __init__(self, browser, p=None):
        self.Task = task.Task_web
        self.wantedLength = 10  # wanted length of task data
        self.browser = browser
        if p != None:
            self.project = p
        else:
            self.project = project.Project(url=self.browser.name)

        self.name = browser.name
        self.logger = logging.getLogger('boinc.browser.{}'.format(self.__class__.__name__))

    @staticmethod
    def getParser(section, **kwargs):
        """Factory for returning the correct subclass based on section name"""
        if section == 'worldcommunitygrid.org':
            logger.debug('getting worldcommunitygrid.org parser')
            parser = HTMLParser_worldcommunitygrid(**kwargs)
        elif section == 'www.rechenkraft.net/yoyo':
            logger.debug('getting yoyo parser')
            parser = HTMLParser_yoyo(**kwargs)
        elif section == 'wuprop.boinc-af.org':
            logger.debug('getting wuprop parser')
            parser = HTMLParser_wuprop(**kwargs)
        elif section == 'www.primegrid.com':
            logger.debug('getting primegrid parser')
            parser = HTMLParser_primegrid(**kwargs)
        elif section == 'numberfields.asu.edu/NumberFields':
            logger.debug('getting NumberFields parser')
            parser = HTMLParser_numberfields(**kwargs)
        # elif section == 'escatter11.fullerton.edu/nfs/':
        #     logger.debug('getting nfs parser')
        #     parser = HTMLParser_nfs(**kwargs)
        elif section == 'climateapps2.oerc.ox.ac.uk/cpdnboinc':
            logger.debug('getting climateprediction parser')
            parser = HTMLParser_climateprediction(**kwargs)
        elif section == 'einstein.phys.uwm.edu/':
            logger.debug('getting einstein parser')
            parser = HTMLParser_einstein(**kwargs)
        else:                   # Lets try the generic
            logger.debug('getting generic parser, name = %s', section)
            parser = HTMLParser(**kwargs)

        return parser

    def parse(self, content):
        """Fills up the self.project with applications and tasks
        Assumes the application name is the last column"""
        for row in self.getRows(content):
            try:
                t = self.Task.createFromHTML(row[:-1])
            except Exception as e:
                self.logger.warning('Unable to parse %s as task: "%s"', row, e)
                continue

            application = self.project.appendApplication(row[-1])
            application.tasks.append(t)

    def parseTable(self, soup):
        for tr in soup.find_all('tr'):
            ret = [td.text for td in tr.find_all('td')]

            if len(ret) != 0:
                self.logger.debug('in parseTable, got %s, len = %s, expected %s', ret, len(ret), self.wantedLength)

            if len(ret) == self.wantedLength and ret[0].strip() != '':
                yield ret

    def getRows(self, html):
        """Generator for each row in result table"""
        soup = BeautifulSoup(html)
        for row in self.parseTable(soup):
            self.logger.debug('yielding %s', row)
            yield row

        for additionalPage in self.findNextPage(soup):
            html = self.browser.visit(additionalPage)
            if html != '':
                for row in self.getRows(html): # Recursion!
                    yield row

    def findNextPage(self, soup):
        """Finds links to additional pages of tasks"""
        reg_compiled = re.compile('offset=(\d+)')
        for offset in soup.find_all('a', href=reg_compiled):
            offset_str = re.search(reg_compiled, offset['href']).group(1)
            offset_int = int(offset_str)
            if offset_int != 0:
                yield offset_int

    def parseWorkunit(self, html):
        """Parses the workunit page, currently returns the application name"""
        soup = BeautifulSoup(html)
        for first_td in soup.find_all('td', class_='fieldname'):
            if first_td.text == 'application':
                app_name = first_td.find_next_sibling('td', class_='fieldvalue')
                return app_name.text

    def fieldvalue(self, soup, fieldname):
        """yields fieldvalue for given fieldname"""
        for row in soup.find_all('tr'):
            if row.td is None:
                continue

            first_td = row.td
            _class = first_td.get('class', [''])
            if _class == ['fieldname'] and first_td.text.strip() == fieldname:
                return first_td.find_next_sibling('td')

class HTMLParser_worldcommunitygrid(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(HTMLParser_worldcommunitygrid, self).__init__(*args, **kwargs)
        self.Task = task.Task_web_worldcommunitygrid

    def parse(self, content):
        data = json.loads(content)
        data = data[u'ResultsStatus']
        print data[u'ResultsAvailable']
        for result in data[u'Results']:
            print self.Task.createFromJSON(result)
        
        exit(1)
        # async_data = list()
        # for row in self.getRows(content):
        #     url = self.name + row[0]
        #     workunit = self.browser.visitURL(url)

        #     t = async.Async(self.Task.createFromHTML, row[1:])
        #     app_name = async.Async(self.parseWorkunit, workunit)
        #     async_data.append((t, app_name, url))

        # for t, app_name, url in async_data:
        #     if app_name.ret is None:
        #         self.browser.removeURL(url)
        #     else:
        #         application = self.project.appendApplication(app_name.ret)
        #         application.tasks.append(t.ret)

    def findNextPage(self, soup):
        reg_compiled = re.compile('pageNum=(\d+)')
        for link in soup.table.find_all('a'):
            try:
                reg = re.search(reg_compiled, link['href'])
                page_num = int(reg.group(1))
                if page_num != 1:
                    yield page_num
            except (TypeError, AttributeError):
                pass
    
    def parseTable(self, soup):
        reg_compiled = re.compile("javascript:addHostPopup\('(/ms/device/viewWorkunitStatus.do\?workunitId=\d+)")
        for tr in soup.table.find_all('tr'):
            row = list()
            for td in tr.find_all('td'):
                try:
                    reg = re.match(reg_compiled, td.a['href'])
                    row.append(reg.group(1))
                except (TypeError, AttributeError):
                    pass
                row.append(td.text.strip())

            # logger.debug('len(row)= %s, row = %s', len(row), row)
            if len(row) == 8:
                yield row

    def parseWorkunit(self, html):
        soup = BeautifulSoup(html)
        reg_compiled = re.compile('Project Name:\s*([^\n]+)\n')
        for tr in soup.find_all('tr'):
            for td in tr.find_all('td'):
                reg = re.search(reg_compiled, td.text)
                if reg:
                    return reg.group(1).strip()
        else:
            logger.error('Could not find project name for worldcommunitygrid task %s', soup.prettify())
            return None

    def getBadges(self):
        page = self.browser.visitStatistics()
        self.parseStatistics(page)

    def parseStatistics(self, page):
        """Gets the xml statistics for worldcommunitygrid"""
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
        stat = statistics.ProjectStatistics_worldcommunitygrid(lastResult, *stat)
        self.project.appendStatistics(stat)

        for application in tree.iter('Project'):
            short = application.find('ProjectShortName').text
            name = application.find('ProjectName').text
            runtime = application.find('RunTime').text
            points = application.find('Points').text
            results = application.find('Results').text
            
            app = self.project.appendApplication(name)
            Stat = statistics.ApplicationStatistics_worldcommunitygrid
            app.appendStatistics(Stat(runtime, points, results))

        for b in tree.iter('Badge'):
            name = b.find('ProjectName').text
            url = b.iter('Url').next().text
            t = b.iter('Description').next().text
            Badge = badge.Badge_worldcommunitygrid
            self.project.appendBadge(name, Badge(name=t, url=url))


class HTMLParser_yoyo(HTMLParser_worldcommunitygrid):
    def __init__(self, *args, **kwargs):
        super(HTMLParser_yoyo, self).__init__(*args, **kwargs)
        self.Task = task.Task_web_yoyo

    def parseTable(self, soup):
        for table in soup.find_all('table'):
            for tr in table.find_all('tr'):
                row = list()
                for td in tr.find_all('td'):
                    if td.find('a') != None:
                        name = td.a.get('title')
                        if name is not None:
                            row.append(name.replace('Name: ', ''))

                        url = td.a.get('href', '')
                        if 'workunit' in url:
                            row.append('/'+url)
                    else:
                        row.append(td.text)

                if len(row) == 10:
                    row[0], row[1] = row[1], row[0]
                    yield row

    def findNextPage(self, soup):
        # This is ugly, but we need to bypass the superclass
        return HTMLParser.findNextPage(self, soup)

    def parseWorkunit(self, html):
        # This is ugly, but we need to bypass the superclass
        return HTMLParser.parseWorkunit(self, html)

    def getBadges(self):
        """Fills out project badges"""
        html = self.browser.visitPage('home.php')
        soup = BeautifulSoup(html)
        self.badgeTabel(soup)

    def badgeTabel(self, soup):
        """ Extracts projects table from www.rechenkraft.net/yoyo/home.php"""
        for t in soup.find_all('table'):
            badgeTable = t.table            # The table within a table
            if badgeTable != None:
                for row in badgeTable.find_all('tr'):
                    data = row.find_all('td')
                    if len(data) == 4:
                        name = data[0].text
                        totalCredits = data[1].text.replace(',', '') # thousand seperator
                        workunits = data[2].text
                        if re.match('\d+ \w\w\w \d\d\d\d', data[3].text):
                            # Hack to avoid the "Projects in which you are participating" table.
                            continue

                        app = self.project.appendApplication(name)
                        app.appendStatistics(statistics.ApplicationStatistics(totalCredits,
                                                                              workunits))
                        if data[3].a:
                            b = data[3].a.img['alt']
                            url = data[3].a.img['src']

                            self.project.appendBadge(name, badge.Badge_yoyo(b, url))

class HTMLParser_climateprediction(HTMLParser):
    """Same as web but length is 11"""
    def __init__(self, *args, **kwargs):
        super(HTMLParser_climateprediction, self).__init__(*args, **kwargs)
        self.Task = task.Task_web_climateprediction
        self.wantedLength = 11
        self.name = 'climateprediction.net'
        self.project.setName(self.name)
        self.project.setUrl('http://www.climateprediction.net')

class HTMLParser_einstein(HTMLParser):
    """Same as web but length is 11"""
    def __init__(self, *args, **kwargs):
        super(HTMLParser_einstein, self).__init__(*args, **kwargs)
        self.Task = task.Task_web_climateprediction
        self.wantedLength = 11

class HTMLParser_primegrid(HTMLParser):
    def getBadges(self):
        """Fills out project badges"""
        html = self.browser.visitPage('home.php')
        soup = BeautifulSoup(html)
        for app_name, badge in self.parseHome(soup):
            self.project.appendBadge(app_name, badge)

        self.parseStatistics(soup)

    def parseHome(self, soup):
        """yields app name and Badge object"""
        for fieldvalue in self.fieldvalue(soup, 'Badges'):
            yield self.parseBadge(fieldvalue)

    def parseBadge(self, soup):
        """
        Expects something like this:
        <a href="/show_badges.php?userid=222267">
        <img alt="PPS Sieve Bronze: More than 20,000 credits (30,339)" class="badge" 
        src="/img/badges/sr2sieve_pps_bronze.png" title="PPS Sieve Bronze: More than 20,000 credits (30,339)"/>
        </a>
        """
        url = str(self.browser.name)
        url += soup.img.get('src')
        name = soup.img.get('title')
        b = badge.Badge_primegrid(name=name,
                                  url=url)
        self.logger.debug('Badge %s', b)
        return b.app_name, b

    def parseStatistics(self, soup):
        """Tries to parse the application table at home.php"""
        table = soup.find_all('table')[-2] # Hack
        stat = None

        for td in table.find_all('td'):
            class_ = td.get('class')
            if class_ == ['heading']:
                if stat is not None:
                    self.project.appendStatistics(stat) # Append previous

                stat = statistics.ProjectStatistics_primegrid()
                stat['name'] = td.text

            elif class_ == ['fieldname']:
                fieldname = td.text
            elif class_ == ['fieldvalue']:
                fieldvalue = td.text
                stat[fieldname] = fieldvalue

        if stat is not None:
            self.project.appendStatistics(stat) # Append last

        # for app in self.project.applications:
        #     print self.project.applications[app]
        # assert False

class HTMLParser_wuprop(HTMLParser):
    def getBadges(self):
        page = self.browser.visitHome()
        soup = BeautifulSoup(page)
        for b in self.fieldvalue(soup, 'Badge'):
            badge = self.parseBadge(b)
            self.project.appendBadge(badge=badge)

    def parseBadge(self, soup):
        """
        Expects something like this:
        <img src="img/badge/100_0_0_0_0.png"/>
        """
        url = str(self.browser.name).replace('www.', '') + '/' # http://wuprop.boinc-af.org/
        name = soup.get('src')
        url += name
        b = badge.Badge_wuprop(name=name,
                               url=url)
        self.logger.debug('Badge %s', b)
        return b
    

    def projectTable(self, html):
        """ Extracts projects table from wuprop.boinc-af.org/home.php"""
        projects = dict()       # Key is user_friendly_name!
        soup = BeautifulSoup(html)
        t = soup.find_all('table')
        for row in t[-1].find_all('tr'):
            data = row.find_all('td')
            if len(data) == 4:
                proj_name = data[0].text
                app_name = data[1].text
                runningTime = data[2].text
                pending = data[3].text
                stat = statistics.ApplicationStatistics_wuprop(runtime=runningTime,
                                                               pending=pending)
                if proj_name not in projects:
                    projects[proj_name] = project.Project(name=proj_name)

                logger.debug('app_name %s', app_name)
                app = projects[proj_name].appendApplication(app_name, is_long=True)
                app.appendStatistics(stat)
                #self.project = Project(short=projects, name=application, wuRuntime=runningTime, wuPending=pending)

        return projects

class HTMLParser_numberfields(HTMLParser):
    Badge = badge.Badge_numberfields

    def getBadges(self):
        page = self.browser.visitHome()
        self.parseHome(page)
        
    def parseHome(self, html): 
        soup = BeautifulSoup(html)
        for first_td in soup.find_all('td', class_='fieldname'):
            fieldname = first_td.text.strip()
            if fieldname == 'Badges':
                b = first_td.find_next_sibling('td', class_='fieldvalue')
                img = b.find('img')
                if img is None:
                    continue
                
                try:
                    url = img['src']
                    name = img['title']
                    b = self.Badge(name=name, url=url)
                    self.project.appendBadge(badge=b)
                except KeyError as e:
                    continue
            elif fieldname == 'Total credit':
                v = first_td.find_next_sibling('td', class_='fieldvalue').text
                v = v.replace(',', '')
                self.project.credit = float(v)

class HTMLParser_nfs(HTMLParser_numberfields):
    Badge = badge.Badge_nfs
