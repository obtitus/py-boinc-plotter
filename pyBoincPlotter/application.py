# Standard import
import re
# non standard
from bs4 import BeautifulSoup

class Application(object):
    def __init__(self, name, badge='', statistics=''):
        self.name = name                # Hopefully on the form Say No to Schistosoma (sn2s)
        self.tasks = list()
        self.badge = badge
        self.statistics = statistics

    def setNameFromXML(self, xml):
        """
        Expects the application block:
        <app>
        ...
        </app>
        from the boinc rpc
        """        
        soup = BeautifulSoup(xml, "xml")
        self.setNameFromSoup(soup)

    def setNameFromSoup(self, soupe):
        self.name_short = soup.find('name').text   # Vops: soup.name is 'reserved' so need to use find('name')
        self.name_long  = soup.find('user_friendly_name').text

        self._name = "{} ({})".format(long, short)

    
    # Name
    """Name should be on the form <long> (<short>), do a regexp when the name is set.
    name_long returns <long> and name_short returns <short>"""
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
        reg = re.findall('([^(]+)\((\w+)\)', name)
        if reg != []:
            reg = reduce(lambda x,y: x+y, reg) # flatten list
            self.name_long = "".join(reg[:-1]).strip()
            self.name_short = reg[-1].strip()
        else:
            self.name_long = self._name
            self.name_short = ''

    def __str__(self):
        return str(self.name)
