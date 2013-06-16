import unittest

import applications

class TestApplications(unittest.TestCase):
    def setUp(self):
        self.app = applications.Application('foo (bar)', '')

    def test_name(self):
        self.assertEqual(self.app.name_long, 'foo')
        self.assertEqual(self.app.name_short, 'bar')
        self.assertEqual(self.app.name, 'foo (bar)')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplications)
    unittest.TextTestRunner(verbosity=2).run(suite)
