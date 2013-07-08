# Non-standard python
from bs4 import BeautifulSoup
# This project
import task
import async

class HTMLParser(object):
    def __init__(self, name, browser):
        self.Task = task.Task_web
        self.browser = browser
        self.name = name

    @staticmethod
    def getParser(section, browser):
        kwargs = dict(name=section, browser=browser)
        if section == 'worldcommunitygrid.org':
            parser = HTMLParser_worldcommunitygrid(**kwargs)
        else:                   # Lets try the generic
            parser = HTMLParser(**kwargs)

        return parser

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

    def parse(self):
        project = Project(self.name)
        content = self.visit()
        for row in self.getRows(content):
            t = self.Task.createFromHTML(row[:-1])
            application = project.appendApplication(row[-1])
            application.tasks.append(t)

        return project
        
    def parseAdditionalPages(self, soup):
        reg_compiled = re.compile('offset=(\d+)')
        for link in soup.table.find_all('a'):
            try:
                reg = re.search(reg_compiled, link['href'])
                if int(reg.group(1)) != 0:
                    yield reg.group(1)
            except (TypeError, AttributeError):
                pass
    
    def parseTable(self, soup):
        #print 'parseTable', soup.prettify()
        for tr in soup.table.find_all('tr'):
            try:
                if tr['class'][0].startswith('row0'):
                    yield [td.text for td in tr.find_all('td')]
            except KeyError:
                pass

        # reg_compiled = re.compile("javascript:addHostPopup\('(/ms/device/viewWorkunitStatus.do\?workunitId=\d+)")
        # for tr in soup.table.find_all('tr'):
        #     row = list()
        #     for td in tr.find_all('td'):
        #         try:
        #             reg = re.match(reg_compiled, td.a['href'])
        #             row.append(reg.group(1))
        #         except (TypeError, AttributeError):
        #             pass
        #         row.append(td.text.strip())

        #     if len(row) == 8:
        #         yield row

    def parseWorkunit(self, html):
        soup = BeautifulSoup(html)
        print 'parseWorkunit', soup.prettify()
        # reg_compiled = re.compile('Project Name:\s*([^\n]+)\n')
        # for tr in soup.find_all('tr'):
        #     for td in tr.find_all('td'):
        #         reg = re.search(reg_compiled, td.text)
        #         if reg:
        #             return reg.group(1).strip()

class HTMLParser_worldcommunitygrid(HTMLParser):
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
