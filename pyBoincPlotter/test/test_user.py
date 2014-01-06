
# This file is part of the py-boinc-plotter,
# which provides parsing and plotting of boinc statistics and
# badge information.
# Copyright (C) 2013 obtitus@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# END LICENCE
import unittest

import user

class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = user.User('1234', 'secret', 'ola')

    def test_userid(self):
        self.assertEqual(self.app.userid, '1234')
        
    def test_password(self):
        self.assertEqual(self.app.password, 'secret')

    def test_username(self):
        self.assertEqual(self.app.username, 'ola')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUser)
    unittest.TextTestRunner(verbosity=2).run(suite)
