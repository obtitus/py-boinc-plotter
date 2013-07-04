import tempfile
import unittest

import browser
import config
import parse_input

class TestWorldcommunitygrid(unittest.TestCase):
    def setUp(self):
        CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
        dir = parse_input.dataFolder
        #dir = tempfile.mkdtemp()
        self.cache = browser.Browser_file(dir, removeOld=False)
        self.browser = browser.Browser_worldcommunitygrid(self.cache, CONFIG)

    def test_parse(self):
        p = self.browser.parse()
        
    def test_rows(self):
        with open(parse_input.html_worldcommunitygrid, 'r') as content:
            rows = list(self.browser.getRows(content))
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

    def test_parse(self):
        project = self.browser.parse()
        self.assertEqual(len(project), 90)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWorldcommunitygrid)
    unittest.TextTestRunner(verbosity=2).run(suite)
