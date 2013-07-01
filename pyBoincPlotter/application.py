# Standard import
import re
# non standard
from bs4 import BeautifulSoup
# This project
from task import Task_local

class Application(object):
    def __init__(self, name='', badge='', statistics=''):
        self.setName(name)                # Hopefully on the form Say No to Schistosoma (sn2s)
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

    def setNameFromSoup(self, soup):
        self.name_short = soup.find('name').text   # Vops: soup.name is 'reserved' so need to use find('name')
        self.name_long  = soup.find('user_friendly_name').text

        self.name = "{} ({})".format(self.name_long, 
                                      self.name_short)


    def appendTaskFromXML(self, xml):
        t = Task_local.createFromXML(xml)
        self.tasks.append(t)
        return t

    # Name
    """Name should be on the form <long> (<short>), do a regexp when the name is set.
    name_long returns <long> and name_short returns <short>"""
    # @property
    # def name(self):
    #     return self.name

    def setName(self, name):
        self.name = name
        reg = re.findall('([^(]+)\((\w+)\)', name)
        if reg != []:
            reg = reduce(lambda x,y: x+y, reg) # flatten list
            self.name_long = "".join(reg[:-1]).strip()
            self.name_short = reg[-1].strip()
        else:
            self.name_long = self.name
            self.name_short = ''

    def __str__(self):
        ret = [str(self.name)]
        for task in self.tasks:
            ret.append(str(task))
        return "\n".join(ret)
