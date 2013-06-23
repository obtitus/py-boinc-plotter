# Standard python
import re

class Project(object):
    def __init__(self, url, user=None, statistics=None, settings=None):
        self.name = url
        self.user = user
        self.applications = dict()
        self.statistics = statistics
        self.settings = settings
        
    def createFromXML(xml):
        """
        Expects the project block:
        <project>
        ...
        </project>
        from the boinc rpc
        """        
        soup = BeautifulSoup(xml, "xml")
        # For now, settings is just a string
        settings = 'Resource share {:.3g}%'.format(float(soup.resource_share.text))
        if soup.dont_request_more_work is not None:
            settings += ", Don't request more work"
        # Get the statistics
        s = Statistics.createFromSoup(soup)
        return Project(soup.master_url.text, statistics=s, settings=pref)


    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
        self.name_short = name.replace('https://', '')
        self.name_short = self.name_short.replace('http://', '')
        self.name_short = self.name_short.replace('www.', '')
        self.name_short = self.name_short.replace('.org', '')
        if self.name_short[-1] == '/':
            self.name_short = self.name_short[:-1]

    def __str__(self):
        endl = '\n'
        ret = []
        for prop in [self.name_short, self.settings, self.statistics]:
            if prop != None:
                ret.append(str(prop))
        return "\n".join(ret)
