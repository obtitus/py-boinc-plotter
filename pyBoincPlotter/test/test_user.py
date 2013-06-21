import unittest

import user

class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = user.User('1234', 'secret', 'ola')

    def test_name(self):
        self.assertEqual(self.app.userid, '1234')
        self.assertEqual(self.app.password, 'secret')
        self.assertEqual(self.app.username, 'ola')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUser)
    unittest.TextTestRunner(verbosity=2).run(suite)
