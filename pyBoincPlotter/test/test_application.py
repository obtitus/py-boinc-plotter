import unittest

import application

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.app = application.Application('foo (bar)')

    def test_name(self):
        self.assertEqual(self.app.name_long, 'foo')
        self.assertEqual(self.app.name_short, 'bar')
        self.assertEqual(self.app.name, 'foo (bar)')
    
    def test_name(self):
        def test(name, wanted_long, wanted_short):
            self.app = application.Application(name)
            self.assertEqual(self.app.name_short, wanted_short)
            self.assertEqual(self.app.name_long , wanted_long)
            self.assertEqual(self.app.name, name)
        test('PPS (Sieve) v1.39 (cpuPPSsieve)', wanted_long='PPS Sieve v1.39', wanted_short='cpuPPSsieve')

    def test_badge(self):
        self.assertEqual(self.app.badge, '')
    
    def test_badge2(self):
        self.app = application.Application('foo (bar)', badge='bronze')
        self.assertEqual(self.app.badge, 'bronze')

    def test_statistics(self):
        self.assertEqual(self.app.statistics, '')
    
    def test_statistics2(self):
        self.app = application.Application('foo (bar)', statistics='42 days')
        self.assertEqual(self.app.statistics, '42 days')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplication)
    unittest.TextTestRunner(verbosity=2).run(suite)
