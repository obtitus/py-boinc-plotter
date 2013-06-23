# non standard import
from bs4 import BeautifulSoup

class HTMLParser_boinchome():
    def __init__(self):
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
