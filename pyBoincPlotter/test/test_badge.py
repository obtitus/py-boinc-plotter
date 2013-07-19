
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
import unittest
import logging
# Project import
import plot.badge as badge
import config
import browser
import loggerSetup

HOURS = 60*60
DAYS = 24*HOURS

"""
This seems to be an updated record of badge supporting projects:
http://www.setiusa.us/archive/index.php/t-4317.html
Not all are currently supported.
"""


class TestBadge(unittest.TestCase):
    def setUp(self):
        CONFIG, CACHE_DIR, BOINC_DIR = config.set_globals()
        self.browser_cache = browser.Browser_file(CACHE_DIR)

    def worldcommunitygrid(self, name, color, value, url=''):
        self.badge = badge.Badge_worldcommunitygrid(name, url)
        self.assertEqual(self.badge.name, name)
        self.assertEqual(self.badge.url, url)
        self.assertEqual(self.badge.color, color)
        self.assertEqual(self.badge.runtime, value)

    def test_silver(self):
        self.worldcommunitygrid('Silver Level Badge (45 days) for The Clean Energy Project - Phase 2',
                                'silver', 45*DAYS)
        self.worldcommunitygrid('Bronze Level Badge (14 days) for Say No to Schistosoma',
                                '#8C7853', 14*DAYS)

    def wuprop(self, runtime, color, value):
        self.badge = badge.Badge_wuprop(runtime)
        self.assertEqual(self.badge.runtime, runtime)
        self.assertEqual(self.badge.color, color)
        self.assertEqual(self.badge.value, value)
        
    def test_wuprop(self):
        self.wuprop(0, 'k', 0)
        self.wuprop(1000, 'k', 0)
        self.wuprop(100*HOURS, '#8C7853', 100)
        self.wuprop(101*HOURS, '#8C7853', 100)
        self.wuprop(250*HOURS, 'silver', 250)
        self.wuprop(500*HOURS, 'gold', 500)
        self.wuprop(1000*HOURS, 'r', 1000)
        self.wuprop(2500*HOURS, 'g', 2500)
        self.wuprop(5000*HOURS, 'b', 5000)

    def yoyo(self, name, color, value, url=''):
        self.badge = badge.Badge_yoyo(name, '')
        self.assertEqual(self.badge.name, name)
        self.assertEqual(self.badge.url, url)
        self.assertEqual(self.badge.color, color)
        self.assertEqual(self.badge.value, value)

    def test_yoyo(self):
        self.yoyo('bronze badge', '#8C7853', 10000)
        self.yoyo('silver badge', 'silver', 100000)
        self.yoyo('gold badge', 'gold', 500000)
        self.yoyo('master badge', 'gold', 1000000)
        self.yoyo('grandmaster badge', 'b', 2000000)
        self.yoyo('guru badge', 'b', 5000000)
        self.yoyo('spirit badge', 'r', 10000000)
        self.yoyo('held badge', 'r', 25000000)
        self.yoyo('half god badge', 'g', 50000000)
        self.yoyo('god badge', 'g', 100000000)

    def test_image(self):
        # Test that it doesn't crash
        b = badge.Badge('foobar', 'http://www.worldcommunitygrid.org/images/pb/cep2_1.jpg')
        self.browser = browser.BrowserSuper(self.browser_cache)
        artist = b.getImageArtist(self.browser, (1, 42), frameon=False, box_alignment=(0, 0.5))

    def primegrid(self, name, color, value, url=''):
        self.badge = badge.Badge_primegrid(name, '')
        self.assertEqual(self.badge.name, name)
        self.assertEqual(self.badge.url, url)
        self.assertEqual(self.badge.color, color)
        self.assertEqual(self.badge.value, value)
    
    def test_primegrid(self):
        self.primegrid('Woodall LLR Bronze: More than 10,000 credits (17,517)',
                       '#8C7853', 10000)
        self.primegrid('PPS Sieve Bronze: More than 20,000 credits (30,339)',
                       '#8C7853', 20000)
        
if __name__ == '__main__':
    loggerSetup.loggerSetup(logging.INFO)
    
    unittest.main()
