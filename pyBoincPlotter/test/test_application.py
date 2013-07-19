
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
# Standard python
import unittest
# This project
import application
import parse_input

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.app = application.Application('foo (bar)')

    def test_name(self):
        self.assertEqual(self.app.name_long, 'foo')
        self.assertEqual(self.app.name_short, 'bar')
        self.assertEqual(self.app.name, 'foo (bar)')
    
    def test_name(self):
        def test(name, wanted_long, wanted_short, wanted_name):
            self.app = application.Application(name)
            self.assertEqual(self.app.name_short, wanted_short)
            self.assertEqual(self.app.name_long , wanted_long)
            self.assertEqual(self.app.name, wanted_name)
        test('PPS (Sieve) v1.39 (cpuPPSsieve)', wanted_long='PPS Sieve', wanted_short='cpuPPSsieve',
             wanted_name='PPS Sieve (cpuPPSsieve)')

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

    def test_task_xml(self):
        self.app.appendTaskFromXML(parse_input.task_active)
        s = str(self.app)
        self.assertEqual(len(s.split('\n')), 2)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplication)
    unittest.TextTestRunner(verbosity=2).run(suite)
