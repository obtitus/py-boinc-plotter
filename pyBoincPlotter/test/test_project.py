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
        self.ignoreSpaces(p.name, 'http://boinc.bakerlab.org/rosetta/')
        self.ignoreSpaces(p.name_short, 'boinc.bakerlab/rosetta')
        self.ignoreSpaces(str(p.statistics), """Total credit,  user: 2 543, host: 2 543, 100%
        Avg credit, user: 227, host: 227, 100%""")

    def test_worldcommunitygrid(self):
        p = Project.createFromXML(parse_input.project_worldcommunitygrid)
        print p
        self.ignoreSpaces(p.name, 'http://www.worldcommunitygrid.org/')
        self.ignoreSpaces(p.name_short, 'worldcommunitygrid')
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
