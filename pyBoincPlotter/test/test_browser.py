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
        project = self.browser.parse()
        print project
        self.assertEqual(len(project), 90)


class TestYoyo(unittest.TestCase):
    def setUp(self):
        CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
        dir = parse_input.dataFolder
        #dir = tempfile.mkdtemp()
        self.cache = browser.Browser_file(dir, removeOld=False)
        self.browser = browser.Browser_yoyo(self.cache, CONFIG)

    # def test_parse(self):
    #     p = self.browser.parse()
        
    # def test_parse(self):
    #     project = self.browser.parse()
    #     self.assertEqual(len(project), 90)


class TestPrimegrid(unittest.TestCase):
    def setUp(self):
        CONFIG = config.setupConfigFile() # TODO: remove this requirement, write browser so that this can be None
        dir = parse_input.dataFolder
        #dir = tempfile.mkdtemp()
        self.cache = browser.Browser_file(dir, removeOld=False)
        self.browser = browser.Browser('www.primegrid.com', 
                                       self.cache, CONFIG)
    
    def test_parse(self):
        project = self.browser.parse()
        self.assertEqual(len(project), 18)
    
if __name__ == '__main__':
    import logging
    from loggerSetup import loggerSetup
    loggerSetup(logging.INFO)

    for t in [TestPrimegrid]:#[TestYoyo, TestWorldcommunitygrid]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        unittest.TextTestRunner(verbosity=2).run(suite)
