# Standard python
import tempfile
import unittest
# This project
import parse
import browser
import config
import parse_input

class TestWorldcommunitygrid(unittest.TestCase):
    def setUp(self):
        CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
        dir = parse_input.dataFolder
        #dir = tempfile.mkdtemp()
        cache = browser.Browser_file(dir, removeOld=False)
        b = browser.Browser_worldcommunitygrid(cache, CONFIG)
        self.parser = parse.HTMLParser_worldcommunitygrid(b)

    def test_rows(self):
        with open(parse_input.html_worldcommunitygrid, 'r') as content:
            rows = list(self.parser.getRows(content))
            self.assertEqual(len(rows), 90)
            print rows[0]
            self.assertEqual(rows[0],
                             ['/ms/device/viewWorkunitStatus.do?workunitId=740179670', 
                              u'faah42222_ ZINC09318874_ xBr27_ refmac2_ A_ PR_ 03_ 0--', 
                              u'coffe.local', 
                              u'In Progress', 
                              u'7/4/13 10:43:39',  u'7/14/13 10:43:39', 
                              u'0.00 / 0.00', u'0.0\xa0/\xa00.0'])
            for r in rows:
                print r

class TestYoyo(unittest.TestCase):
    def setUp(self):
        CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
        dir = parse_input.dataFolder
        #dir = tempfile.mkdtemp()
        cache = browser.Browser_file(dir, removeOld=False)
        b = browser.Browser_yoyo(cache, CONFIG)
        self.parser = parse.HTMLParser_yoyo(b)

    def test_rows(self):
        with open(parse_input.html_yoyo, 'r') as content:
            rows = list(self.parser.getRows(content))
            self.assertEqual(len(rows), 90)
            print rows[0]
            self.assertEqual(rows[0],
                             ['/ms/device/viewWorkunitStatus.do?workunitId=740179670', 
                              u'faah42222_ ZINC09318874_ xBr27_ refmac2_ A_ PR_ 03_ 0--', 
                              u'coffe.local', 
                              u'In Progress', 
                              u'7/4/13 10:43:39',  u'7/14/13 10:43:39', 
                              u'0.00 / 0.00', u'0.0\xa0/\xa00.0'])
            for r in rows:
                print r

class TestPrimegrid(unittest.TestCase):
    def setUp(self):
        CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
        dir = parse_input.dataFolder
        #dir = tempfile.mkdtemp()
        cache = browser.Browser_file(dir, removeOld=False)
        b = browser.Browser('www.primegrid.com', 
                            cache, CONFIG)
        self.parser = parse.HTMLParser(b)
    
    def test_rows(self):
        with open(parse_input.html_primegrid, 'r') as content:
            rows = list(self.parser.getRows(content))
            for r in rows:
                print r

            self.assertEqual(len(rows), 18)
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

if __name__ == '__main__':
    import logging
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)

    for t in [TestPrimegrid]:#[TestYoyo, TestWorldcommunitygrid]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        unittest.TextTestRunner(verbosity=2).run(suite)
