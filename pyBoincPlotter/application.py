import re

class Application(object):
    def __init__(self, name, badge):
        self.name = name                # Hopefully on the form Say No to Schistosoma (sn2s)
        self.tasks = list()
        self.badge = badge
        self.statistics = ?

    # Name
    """Name should be on the form <long> (<short>), do a regexp when the name is set.
    name_long returns <long> and name_short returns <short>"""
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
        reg = re.match('([^(]+)\((\w+)\)', name)
        if reg:
            self.name_long = reg.group(1).strip()
            self.name_short = reg.group(2).strip()
        else:
            self.name_long = self._name
            self.name_short = ''
