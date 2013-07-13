import tempfile
import unittest

import browser
import config
import parse_input

def _setUp(Browser, **kwargs):
    CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
    dir = parse_input.dataFolder
    #dir = tempfile.mkdtemp()
    cache = browser.Browser_file(dir, removeOld=False)
    return Browser(browser_cache=cache, 
                   CONFIG=CONFIG, 
                   **kwargs)


class TestWorldcommunitygrid(unittest.TestCase):
    def setUp(self):
        self.browser = _setUp(browser.Browser_worldcommunitygrid)

    def test_parse(self):
        project = self.browser.parse()
        print project
        self.assertEqual(len(project), 90)

    def test_badge(self):
        xml = self.browser.visitStatistics()
        

class TestYoyo(unittest.TestCase):
    def setUp(self):
        self.browser = _setUp(browser.Browser_yoyo)

    def test_parse(self):
        project = self.browser.parse()
        self.assertEqual(len(project), 21)

class TestPrimegrid(unittest.TestCase):
    def setUp(self):
        self.browser = _setUp(browser.Browser, section='www.primegrid.com')
    
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

class TestMindmodeling(unittest.TestCase):
    def setUp(self):
        self.browser = _setUp(browser.Browser, 
                              section='mindmodeling.org')
    def test_parse(self):
        project = self.browser.parse()
        self.assertEqual(len(project), 7)

if __name__ == '__main__':
    import logging
    from loggerSetup import loggerSetup
    loggerSetup(logging.DEBUG)

    for t in [TestYoyo, TestPrimegrid, TestWorldcommunitygrid]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        unittest.TextTestRunner(verbosity=2).run(suite)
