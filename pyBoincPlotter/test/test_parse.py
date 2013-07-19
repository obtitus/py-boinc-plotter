
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
# Standard python
import tempfile
import unittest
# This project
import parse
import project
import browser
import config
import parse_input
import boinccmd

def _setUp(Browser, Parser, url, **kwargs):
    CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
    dir = parse_input.dataFolder
    #dir = tempfile.mkdtemp()
    cache = browser.Browser_file(dir, removeOld=False)
    b = Browser(browser_cache=cache, 
                CONFIG=CONFIG, 
                **kwargs)
    p = project.Project(url)
    parser = Parser(browser=b, project=p)
    return b, parser

class TestWorldcommunitygrid(unittest.TestCase):
    def setUp(self):
        self.browser, self.parser = _setUp(browser.Browser_worldcommunitygrid,
                                           parse.HTMLParser_worldcommunitygrid,
                                           url='worldcommunitygrid.org')

    def test_rows(self):
        with open(parse_input.html_worldcommunitygrid, 'r') as content:
            rows = list(self.parser.getRows(content))
            for r in rows:
                print r
            self.assertEqual(len(rows), 90)
            self.assertEqual(rows[0],
                             ['/ms/device/viewWorkunitStatus.do?workunitId=740179670', 
                              u'faah42222_ ZINC09318874_ xBr27_ refmac2_ A_ PR_ 03_ 0--', 
                              u'coffe.local', 
                              u'In Progress', 
                              u'7/4/13 10:43:39',  u'7/14/13 10:43:39', 
                              u'0.00 / 0.00', u'0.0\xa0/\xa00.0'])

    def test_badge(self):
        with open(parse_input.xml_worldcommunitygrid, 'r') as page:
            self.parser.parseStatistics(page.read())
            apps = self.parser.project.applications
            for key in apps:
                print key
            
            self.assertEqual('Silver Level Badge (45 days) for The Clean Energy Project - Phase 2',
                             str(apps['The Clean Energy Project - Phase 2'].badge))
            self.assertEqual('Gold Level Badge (90 days) for Human Proteome Folding - Phase 2',
                             str(apps['Human Proteome Folding - Phase 2'].badge))

    def test_parse(self):
        project = self.browser.parse()
        self.assertEqual(len(project), 90)

        apps = project.applications
        for key, app in apps.items():
            print 'KEY', key
            for t in app.tasks:
                print t, t.done()
            print 'TIME', app.pendingTime()

        # These are from the web and therefore should give 0
        self.assertEqual(apps['Computing for Clean Water'].pendingTime(),
                         (0, 0, 0))
        self.assertEqual(apps['The Clean Energy Project - Phase 2'].pendingTime(),
                         (0, 0, 0))

    def test_stats(self):
        project = self.browser.parse()
        apps = project.applications
        self.assertEqual(str(apps['Computing for Clean Water'].statistics),
                         '51 results returned, 20 708 credit, runtime of 5 days, 19:54:04.')
        self.assertEqual(str(apps['Computing for Clean Water'].badge), '')

        self.assertEqual(str(apps['GO Fight Against Malaria'].statistics),
                         '317 results returned, 227 151 credit, runtime of 54 days, 13:01:58.')
        self.assertEqual(str(apps['GO Fight Against Malaria'].badge),
                         'Silver Level Badge (45 days) for GO Fight Against Malaria')

class TestYoyo(unittest.TestCase):
    def setUp(self):
        self.browser, self.parser = _setUp(browser.Browser_yoyo,
                                           parse.HTMLParser_yoyo,
                                           url='www.rechenkraft.net/yoyo')

    def test_rows(self):
        with open(parse_input.html_yoyo, 'r') as content:
            rows = list(self.parser.getRows(content))
            self.assertEqual(len(rows), 21)
            print rows[0]
            self.assertEqual(rows[0],
                             ['/workunit.php?wuid=16671436', 
                              'ogr_130711093650_44_0', 
                              u'11 Jul 2013 19:00:22 UTC', 
                              u'12 Jul 2013 5:24:22 UTC', 
                              u'Over', u'Success', u'Done', 
                              u'16,968.47', u'67.66', u'149.17'])
            for r in rows:
                print r

    def test_parse(self):
        project = self.browser.parse()
        self.assertEqual(len(project), 21)

    def test_badge(self):
        project = self.browser.parse()
        # for key, app in project.applications.items():
        #     print app

        apps = project.applications
        self.assertEqual(str(apps['ecm'].statistics),
                         '19 results returned, 13 754 credit.')
        self.assertEqual(str(apps['ecm'].badge),
                         'bronze badge')

class TestPrimegrid(unittest.TestCase):
    def setUp(self):
        self.browser, self.parser = _setUp(browser.Browser,
                                           parse.HTMLParser_primegrid,
                                           url='www.primegrid.com',
                                           section='www.primegrid.com')
    
    def test_rows(self):
        with open(parse_input.html_primegrid, 'r') as content:
            rows = list(self.parser.getRows(content))
            for r in rows:
                print r

            self.assertEqual(35, len(rows))
            print rows[0]
            self.assertEqual(rows[0],
                             [u'pps_sr2sieve_62137943_1', 
                              u'341870062', 
                              u'398084', 
                              u'5 Jul 2013 | 6:44:08 UTC', 
                              u'11 Jul 2013 | 6:44:08 UTC', 
                              u'In progress', 
                              u'---', u'---', u'---', 
                              u'PPS (Sieve) v1.39 (cpuPPSsieve)'])

    def test_parse(self):
        project = self.browser.parse()
        self.assertEqual(35, len(project))

    def test_badge(self):
        p = self.browser.parse()
        self.assertEqual(len(p.badge), 2)
        self.assertEqual(str(p.badge[1]), 'Woodall LLR Bronze: More than 10,000 credits (17,517)')
        self.assertEqual(str(p.badge[0]), 'PPS Sieve Bronze: More than 20,000 credits (30,339)')
        self.assertEqual(p.badge[1].url, 'http://www.primegrid.com/img/badges/woo_bronze.png')
        self.assertEqual(p.badge[0].url, 'http://www.primegrid.com/img/badges/sr2sieve_pps_bronze.png')

    def test_stats(self):
        project = self.browser.parse()
        self.assertEqual(str(project.statistics), """321 Prime Search tasks (LLR), 4 results returned, 6,259.83 credits
LLR Woodall tests, 4 results returned, 17,517.29 credits
Proth Prime Search (sieve) tasks, 9 results returned, 30,339.00 credits, Factors found 25 (avg. 2.7778/task)
Proth Prime Search (PPS & PPSE) tasks, 23 results returned, 1,120.97 credits
Sophie Germain Prime Search tasks, 18 results returned, 718.44 credits
The Riesel Problem (Sieve) tasks, 4 results returned, 2,293.62 credits, Factors found 1 (avg. 0.25/task)""")

        # self.assertEqual(str(apps['Woodall'].statistics),
        #                  '4 results returned, 17 517.29 credits')
        # self.assertEqual(str(apps['Woodall'].statistics),
        #                  '4 results returned, 17 517.29 credits')

class TestWuprop(unittest.TestCase):
    def setUp(self):
        self.browser, self.parser = _setUp(browser.Browser,
                                           parse.HTMLParser_wuprop,
                                           url='wuprop.boinc-af.org',
                                           section='wuprop.boinc-af.org')

    def test_stat(self):
        html = self.browser.visitHome()
        projects = self.parser.projectTable(html)

        for key, p in projects.items():
            print key, p

        p = projects['World Community Grid'] # Vops, note that key is not url
        app = p.applications['Drug Search for Leishmaniasis']
        self.assertTrue(str(app.statistics),
                        'WuProp runtime 70 days, 18:30:00')

        p = projects['MindModeling@Beta'] # Vops, note that key is not url
        app = p.applications['Native Pypy Application']
        self.assertTrue(str(app.statistics),
                        'WuProp runtime 3:58:48')

    def test_merge(self):
        # todo: avoid duplicate
        CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
        dir = parse_input.dataFolder
        browser_cache = browser.Browser_file(dir, removeOld=False)

        wuprop_projects = browser.getProjects_wuprop(CONFIG, browser_cache)
        #web_projects    = browser.getProjectsDict(CONFIG, browser_cache)
        local_projects = boinccmd.get_state() # TODO: must replace this with file based

        p = project.pretty_print
        # print 'Before merge'
        # print 'WU:', 
        # p(wuprop_projects)
        # print 'WEB:', 
        # p(local_projects)
        
        project.mergeWuprop(wuprop_projects,
                            local_projects)
        print 'After merge'
        p(local_projects)

        assert False            # not done

class TestMindmodeling(unittest.TestCase):
    def setUp(self):
        self.browser, self.parser = _setUp(browser.Browser,
                                           parse.HTMLParser,
                                           url='mindmodeling.org',
                                           section='mindmodeling.org')

    def test_parse(self):
        project = self.browser.parse()
        self.assertEqual(len(project), 7)

class TestNumbersFields(unittest.TestCase):
    def setUp(self):
        self.browser, self.parser = _setUp(browser.Browser,
                                           parse.HTMLParser,
                                           url='numberfields.asu.edu/NumberFields',
                                           section='numberfields.asu.edu/NumberFields')
    
    def test_parse(self):
        project = self.browser.parse()
        print project
        self.assertEqual(len(project), 1)
    
if __name__ == '__main__':
    import logging
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)

    for t in [TestNumbersFields]:#[TestYoyo, TestPrimegrid, TestWorldcommunitygrid, TestWuprop]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        unittest.TextTestRunner(verbosity=2).run(suite)
