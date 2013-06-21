import unittest

import application

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.app = application.Application('foo (bar)')

    def test_name(self):
        self.assertEqual(self.app.name_long, 'foo')
        self.assertEqual(self.app.name_short, 'bar')
        self.assertEqual(self.app.name, 'foo (bar)')
    
    def test_badge(self):
        self.assertEqual(self.app.badge, '')
    
    def test_badge2(self):
        self.app = application.Application('foo (bar)', badge='bronze')
        self.assertEqual(self.app.badge, 'bronze')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplication)
    unittest.TextTestRunner(verbosity=2).run(suite)
