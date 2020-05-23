
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
# Standard python imports
import os
import re
import datetime
from io import StringIO
# try:
#     from cStringIO import StringIO
# except:
#     from StringIO import StringIO
# Scientific import
from .importMatplotlib import *

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
        elif name == 'amethyst': name = (149/255., 39/255., 197/255.)
        elif name == 'turquoise': name = (59/255., 215/255., 249/255.)
        elif name == 'diamond': name = (142/255., 219/255., 245/255.)
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
        zoom = kwargs.pop('zoom', 1)
        try:
            img = browser.visitURL(self.url, extension=extension)
            img = StringIO(img)
            img = mpimg.imread(img, format=extension) # may raise error due to .jpg, support for other images than .png is added by PIL
            #if max(img.size) > maxdim:
            img.resize((maxdim, maxdim))
            # Add image:
            of = matplotlib.offsetbox.OffsetImage(img, zoom=zoom)
            ab = matplotlib.offsetbox.AnnotationBbox(of, *args, **kwargs)
            return ab                   # use plt.gca().add_artist(ab)
        except Exception:
            logger.exception('Badge image failed, url = %s, extension = %s', self.url, extension)
            
class Badge_worldcommunitygrid(Badge):
    @Badge.name.setter
    def name(self, name):
        self._name = name
        name = name.replace('Level Badge', 'Badge') # hack.., the diamond++ badges is without the 'Level Badge'
        self.reg = re.search('(\w+) Badge \((\d+) (days|year|years)\)', name)
        logger.debug("Badge_worldcommunitygrid %s, %s", name, self.reg)
    
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
            if reg.group(3).startswith('year'):
                years = int(reg.group(2))
                day = datetime.timedelta(days=years*365.25).total_seconds()
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
              [5000, 'Sapphire'],
              [10000, 'Magenta'],
              [25000, 'Lime'],
              [50000, 'Cyan'],
              [100000, 'Purple']]
    def __init__(self, name='', url=''):
        self.name = name
        self.url = url
        self.isWuprop = True    # isinstance failed, see http://mail.python.org/pipermail/python-bugs-list/2005-August/029861.html

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @Badge.name.setter
    def name(self, url):
        reg = re.search('(\d+)_(\d+)_(\d+)_(\d+)_(\d+)', url)
        if reg:
            name = 'Badge: '
            for ix, group in enumerate(reg.groups()):
                if group != '0':
                    name += "{} applications: {} hours, ".format((ix+1)*20, group)
            self._name = name[:-2]
            self.value = map(int, reg.groups())
        else:
            self._name = url

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

class Badge_numberfields(Badge):
    badges = [[10000, 'Bronze'],
              [100000, 'Silver'],
              [500000, 'Gold'],
              [1000000, 'Sapphire'],
              [10000000, 'Ruby'],
              [50000000, 'Emerald'],
              [100000000, 'Diamond']]
    # 'Bronze Medal- 10k credits. (Next badge is Silver at 100k)'
    reg = '(\w+) Medal[-\s]*(\d+)(\w) credits'

    def setValue(self, value, suffix):
        value = float(value)
        if suffix == 'k':
            value *= 1000
        elif suffix == 'm':
            value *= 1000000
        else:
            logger.warning('Unknown numbersfields badge suffix %s, "%s"', reg.group(3), name)
        return value

    @Badge.name.setter
    def name(self, name):
        self._name = name
        if name == '': return 

        reg = re.search(self.reg, name)
        if reg:
            self.color = self.badgeToColor(reg.group(1))
            self.value = self.setValue(value=reg.group(2), 
                                       suffix=reg.group(3))
        else:
            logger.warning('Regexp failed on badge string "%s"', name)

class Badge_nfs(Badge_numberfields):
    badges = [[10000, 'Bronze'],
              [100000, 'Silver'],
              [500000, 'Gold'],
              [1000000, 'Amethyst'],
              [5000000, 'Turquoise'],
              [10000000, 'Sapphire'],
              [50000000, 'Ruby'],
              [100000000, 'Emerald'],
              [500000000, 'Diamond']]

    # 10k in NFS credit
    reg = '(\d+)(\w) in NFS credit'

    @Badge.name.setter
    def name(self, name):
        self._name = name
        if name == '': return

        reg = re.search(self.reg, name)
        if reg:
            self.value = self.setValue(value=reg.group(1),
                                       suffix=reg.group(2))
        else:
            logger.warning('Regexp failed on badge string "%s"', name)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = 'http://escatter11.fullerton.edu/nfs/'+url
        if url == '': return

        reg = re.search('(\w+)_nfs.png', url)
        if reg:
            self.color = self.badgeToColor(reg.group(1))
        else:
            logger.warning('Regexp failed on badge url "%s"', url)
