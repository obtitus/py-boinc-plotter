# Standard python imports
import os
import re
import datetime
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
# Scientific import
from importMatplotlib import *

# logger
import logging
logger = logging.getLogger('boinc.badge')
        
class Badge(object):
    # Define:
    # self.color and self.value in subclass
    def __init__(self, name, url):
        self.name = name
        self.url = url

    @staticmethod
    def badgeToColor(name):
        name = name.lower()
        if name == 'bronze': name = '#8C7853'
        elif name == 'ruby': name = 'r'
        elif name == 'emerald': name = 'g'
        elif name == 'sapphire': name = 'b'
        # yoyo colors
        elif name == 'master': name = 'gold'
        elif name == 'grandmaster': name = 'b'
        elif name == 'guru': name = 'b'
        elif name == 'spirit': name = 'r'
        elif name == 'held': name = 'r'
        elif name == 'half god': name = 'g'
        elif name == 'god': name = 'g'        
        return name

    # Overriden in subclass:
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name

    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self.__class__) + self.name

    def getImageArtist(self, browser, *args, **kwargs):
        # Uses badge url to create a matplotlib artist where the
        # matplotlib.offsetbox.AnnotationBbox
        # is created by *args and **kwargs. Typical usage: (ix, day), frameon=False, box_alignment=(0, 0.5)
        fileName, extension = os.path.splitext(self.url)        
        try:
            img = browser.visitURL(self.url, extension=extension)
            img = StringIO(img)
            img = mpimg.imread(img, format=extension) # may raise error due to .jpg, support for other images than .png is added by PIL
            # Add image:
            of = matplotlib.offsetbox.OffsetImage(img)
            ab = matplotlib.offsetbox.AnnotationBbox(of, *args, **kwargs)
            return ab                   # use plt.gca().add_artist(ab)
        except Exception:
            logger.exception('Badge image failed, url = %s, extension = %s', self.url, extension)
            
class Badge_worldcommunitygrid(Badge):
    @Badge.name.setter
    def name(self, name):
        self._name = name
        self.reg = re.search('(\w+) Level Badge \((\d+) (days|years)\)', name)
    
    @property
    def color(self):
        reg = self.reg
        if reg:
            return Badge.badgeToColor(reg.group(1))
        else:
            return 'k'
        
    @property
    def runtime(self):
        reg = self.reg
        if reg:
            if reg.group(3) == 'years':
                year = int(reg.group(2))
                day = datetime.timedelta(years=years).total_seconds()
            elif reg.group(3) == 'days':
                day = int(reg.group(2))
                day = datetime.timedelta(days=day).total_seconds()
            else:
                logger.error('Badge level not recognized "%s", "%s"', self.name, reg.groups()) # TODO: raise exception?
                return 0
            return day
        else:
            return 0

class Badge_wuprop(Badge):
    # Example url: http://wuprop.boinc-af.org/img/badge/100_0_0_0_0.png
    badges = [[100, 'Bronze'],
              [250, 'Silver'],
              [500, 'Gold'],
              [1000, 'Ruby'],
              [2500, 'Emerald'],
              [5000, 'Sapphire']]
    def __init__(self, runtime, name='', url=''):
        self.runtime = runtime
        self.name = name
        self.url = url

    @property
    def runtime(self):
        return self._runtime
    @runtime.setter
    def runtime(self, value):
        self._runtime = value
        self.color, self.value = Badge_wuprop.getColor(self.runtime)

    @staticmethod
    def getColor(runtime):
        # color and value based on runtime (in seconds)
        color = 'k'
        value = 0
        for b, c in Badge_wuprop.badges:
            if runtime >= b*60*60:
                color = Badge.badgeToColor(c);
                value = b
        return color, value
        
class Badge_yoyo(Badge):
    badges = {'bronze': 10000,
              'silver': 100000,
              'gold': 500000,
              'master': int(1e6),
              'grandmaster': int(2e6),
              'guru': int(5e6),
              'spirit': int(10e6),
              'held': int(25e6),
              'half god' : int(50e6),
              'god': int(100e6)}

    @Badge.name.setter
    def name(self, name):
        self._name = name
        self.reg = re.search('([\w\s]+) badge', name)

    @property
    def color(self):
        reg = self.reg
        if reg:
            return Badge.badgeToColor(reg.group(1))
        else:
            return 'k'
        
    @property
    def value(self):
        reg = self.reg
        if reg:
            try:
                return self.badges[reg.group(1)]
            except KeyError:
                logger.error('Badge level not recognized "%s", "%s"', self.name, reg.groups()) # TODO: raise exception?
                return 0
        else:
            return 0
    
class Badge_primegrid(Badge):
    @Badge.name.setter
    def name(self, name):
        self._name = name
        self.reg = re.search('(\w+ \w+) (\w+): More than ([\d,]+) credits \(([\d,]+)\)', name)

    @property
    def color(self):
        reg = self.reg
        if reg:
            return Badge.badgeToColor(reg.group(2))
        else:
            return 'k'
    
    def _getFloat(self, groupId):
        reg = self.reg
        if reg:
            c = reg.group(groupId).replace(',', '')
            return float(c)
        else:
            return 0

    @property
    def value(self):
        return self._getFloat(3)

    @property
    def credit(self):
        return self._getFloat(4)

    @property
    def app_name(self):
        if self.reg:
            return self.reg.group(1)
        else:
            return 'Unknown'
