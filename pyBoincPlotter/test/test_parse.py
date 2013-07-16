# Standard python
import tempfile
import unittest
# This project
import parse
import project
import browser
import config
import parse_input

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

class TestWuprop(unittest.TestCase):
    def setUp(self):
        self.browser, self.parser = _setUp(browser.Browser,
                                           parse.HTMLParser_wuprop,
                                           url='wuprop.boinc-af.org',
                                           section='wuprop.boinc-af.org')

if __name__ == '__main__':
    import logging
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)

    for t in [TestYoyo, TestPrimegrid, TestWorldcommunitygrid]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        unittest.TextTestRunner(verbosity=2).run(suite)
