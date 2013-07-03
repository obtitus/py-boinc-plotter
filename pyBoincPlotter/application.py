# Standard import
import re
# non standard
from bs4 import BeautifulSoup
# This project
from task import Task_local

class Application(object):
    def __init__(self, name='', badge='', statistics=''):
        self.setName_shortLong(name)                # Hopefully on the form Say No to Schistosoma (sn2s)
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

    def setName_shortLong(self, name):
        """
        Sets self.name_long and self.name_short based on the following pattern
        <long> (<short>)
        """
        self.name = name
        reg = re.findall('([^(]+)\((\w+)\)', name)
        if reg != []:
            reg = reduce(lambda x,y: x+y, reg) # flatten list
            name_long = "".join(reg[:-1]).strip()
            name_short = reg[-1].strip()
        else:
            name_long = self.name
            name_short = ''
        
        self.setName_long(name_long)
        self.name_short = name_short

    def setName_long(self, name_long=None):
        """
        Removes the version part of the application long name (if any)
        """
        if name_long is None: name_long = self.name_long
        
        reg = re.search('(v\d+.\d+)', name_long)
        if reg:
            s = reg.start()
            e = reg.end()
            self.version = reg.group()
            name_long = name_long[:s] + name_long[e:]
        else:
            name_long = name_long
        self.name_long = name_long.strip()

    def __str__(self):
        ret = ["= {} =".format(self.name)]
        for task in self.tasks:
            ret.append(str(task))
        return "\n".join(ret)

    def __len__(self):
        """
        Number of tasks
        """
        return len(self.tasks)
