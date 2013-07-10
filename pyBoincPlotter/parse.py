# Standard
import re
import logging
logger = logging.getLogger('boinc.browser')

# Non-standard python
from bs4 import BeautifulSoup
# This project
import task
import plot.badge as badge
import async

class HTMLParser(object):
    def __init__(self, browser):
        self.Task = task.Task_web
        self.browser = browser
        self.name = browser.name

    @staticmethod
    def getParser(section, browser):
        kwargs = dict(browser=browser)
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
        else:                   # Lets try the generic
            logger.debug('getting generic parser, name = %s', section)
            parser = HTMLParser(**kwargs)

        return parser

    def parse(self, content, project):
        for row in self.getRows(content):
            t = self.Task.createFromHTML(row[:-1])
            application = project.appendApplication(row[-1])
            application.tasks.append(t)

        return project

    def getRows(self, html):
        """Generator for each row in result table"""
        soup = BeautifulSoup(html)
        for row in self.parseTable(soup):
            yield row

        for additionalPage in self.parseAdditionalPages(soup):
            html = self.browser.visit(additionalPage)
            if html != '':
                soup = BeautifulSoup(html)
                for row in self.parseTable(soup):
                    yield row

    def parseTable(self, soup):
        #print 'parseTable', soup.prettify()
        for tr in soup.table.find_all('tr'):
            try:
                if tr['class'][0].startswith('row0'):
                    yield [td.text for td in tr.find_all('td')]
            except KeyError:
                pass
        
    def parseAdditionalPages(self, soup):
        reg_compiled = re.compile('offset=(\d+)')
        for link in soup.table.find_all('a'):
            try:
                reg = re.search(reg_compiled, link['href'])
                if int(reg.group(1)) != 0:
                    yield reg.group(1)
            except (TypeError, AttributeError):
                pass

class HTMLParser_worldcommunitygrid(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(HTMLParser_worldcommunitygrid, self).__init__(*args, **kwargs)
        self.Task = task.Task_web_worldcommunitygrid

    def parse(self, content, project):
        async_data = list()
        for row in self.getRows(content):
            url = self.name + row[0]
            workunit = self.browser.visitURL(url)

            t = async.Async(self.Task.createFromHTML, row[1:])
            app_name = async.Async(self.parseWorkunit, workunit)
            async_data.append((t, app_name))

        for t, app_name in async_data:
            application = project.appendApplication(app_name.ret)
            application.tasks.append(t.ret)

        return project

    def parseAdditionalPages(self, soup):
        reg_compiled = re.compile('pageNum=(\d+)')
        for link in soup.table.find_all('a'):
            try:
                reg = re.search(reg_compiled, link['href'])
                yield reg.group(1)
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

class HTMLParser_yoyo(HTMLParser):
    def badgeTabel(self, soup):
        """ Extracts projects table from www.rechenkraft.net/yoyo"""
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

                        badge = ''
                        badgeURL = None
                        if data[3].a:
                            badge = data[3].a.img['alt']
                            badgeURL = data[3].a.img['src']

                        self.projects[name] = Project(name=name, points=totalCredits, results=workunits, 
                                                      badge=badge, badgeURL=badgeURL)

class HTMLParser_wuprop(HTMLParser):
    def badgeTabel(self, soup):
        """ Extracts projects table from wuprop.boinc-af.org/home.php"""
        t = soup.find_all('table')
        for row in t[-1].find_all('tr'):
            data = row.find_all('td')
            if len(data) == 4:
                projects = data[0].text
                application = data[1].text
                runningTime = float(data[2].text)*60*60
                pending = float(data[3].text)*60*60
                self.projects[application] = Project(short=projects, name=application, wuRuntime=runningTime, wuPending=pending)

class HTMLParser_primegrid(HTMLParser):
    def getBadges(self):
        html = self.browser.visitPage('home.php')
        soup = BeautifulSoup(html)
        for row in soup.find_all('tr'):
            if row.td is None:
                continue
                
            first_td = row.td
                
            if first_td.get('class') == ['fieldname'] and first_td.text == 'Badges':
                for badge in first_td.find_next_sibling('td').find_all('a'):
                    yield self.parseBadge(badge)

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
        logger.debug('Badge %s', b)
        return b
        
def parse_worldcommunitygrid_xml(page):
    # TODO: convert to beautiful-soup?
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
