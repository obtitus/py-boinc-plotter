import tempfile
import unittest

import browser
import config
import parse_input

class TestWorldcommunitygrid(unittest.TestCase):
    def setUp(self):
        CONFIG = config.setupConfigFile() # TODO
        dir = parse_input.thisFolder
        #dir = '/Users/ob/Programming/Python/src/boinc2/pyBoincPlotter/test'
        #dir = tempfile.mkdtemp()
        self.cache = browser.Browser_file(dir, removeOld=False)
        self.browser = browser.Browser_worldcommunitygrid(self.cache, CONFIG)

    def test_parse(self):
        p = self.browser.parse()
        
    def test_rows(self):
        with open(parse_input.html_worldcommunitygrid, 'r') as content:
            rows = list(self.browser.getRows(content))
            self.assertEqual(len(rows), 15)
            self.assertEqual(rows[0],
                             ['/ms/device/viewWorkunitStatus.do?workunitId=739866826', 
                              u'DSFL_ X01_ 0000009_ 0337_ 0--', 
                              u'coffe.local', 
                              u'In Progress', 
                              u'7/3/13 19:03:26', 
                              u'7/13/13 19:03:26', 
                              u'0.00 / 0.00', 
                              u'0.0\xa0/\xa00.0'])
            for r in rows:
                print r

    def test_parse(self):
        self.browser.parse()
        assert False

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWorldcommunitygrid)
    unittest.TextTestRunner(verbosity=2).run(suite)
