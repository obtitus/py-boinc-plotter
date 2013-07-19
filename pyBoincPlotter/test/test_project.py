
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

from project import Project
import parse_input

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.proj = Project('http://boinc.bakerlab.org/rosetta/')
    
    def ignoreSpaces(self, s1, s2):
        self.assertEqual(s1.replace(' ', ''),
                         s2.replace(' ', ''))

    def test_rosetta(self):
        p = Project.createFromXML(parse_input.project_rosetta)
        print p
        self.ignoreSpaces(p.name, 'rosetta@home')
        self.ignoreSpaces(p.url, 'http://www.boinc.bakerlab.org/rosetta')
        self.ignoreSpaces(str(p.statistics), """Total credit,  user: 2 543, host: 2 543, 100%
        Avg credit, user: 227, host: 227, 100%""")

    def test_worldcommunitygrid(self):
        p = Project.createFromXML(parse_input.project_worldcommunitygrid)
        print p
        self.ignoreSpaces(p.url, 'http://www.worldcommunitygrid.org')
        self.ignoreSpaces(p.name, 'World Community Grid')
        self.ignoreSpaces(str(p.statistics), """Total credit,  user: 213 009, host: 207 378, 97%
        Avg credit, user: 1 770, host: 1 769, 100%""")

    def test_app(self):
        p = self.proj.appendApplicationFromXML(parse_input.application)
        print p

    def test_workunit(self):
        w = self.proj.appendWorkunitFromXML(parse_input.workunit)
        self.assertEqual(str(w), 'name faah42091_ZINC58026222_xBr27_refmac2_A_PR_01, app_name faah')

    def test_result(self):
        with self.assertRaises(KeyError): # shouldn't work
            w = self.proj.appendResultFromXML(parse_input.task_active)

        self.proj.appendWorkunitFromXML("""<workunit>
        <name>faah41423_ZINC08270033_xBr27_refmac2_A_PR_03</name>
        <app_name>faah</app_name>
        """)
        with self.assertRaises(KeyError): # should still not work
            w = self.proj.appendResultFromXML(parse_input.task_active)

        # should work!
        self.proj.appendApplicationFromXML(parse_input.application)
        w = self.proj.appendResultFromXML(parse_input.task_active)
        s = str(self.proj).split('\n')
        self.assertTrue(len(s), 3)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplication)
    unittest.TextTestRunner(verbosity=2).run(suite)
