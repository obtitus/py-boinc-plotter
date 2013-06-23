import unittest

import parse.boinccmd
import parse_input

class TestApplication(unittest.TestCase):
    # def setUp(self):
    #     self.app = application.Application('foo (bar)')
    
    def ignoreSpaces(self, s1, s2):
        self.assertEqual(s1.replace(' ', ''),
                         s2.replace(' ', ''))

    def test_rosetta(self):
        p = parse.boinccmd.project(parse_input.project_rosetta)
        print p
        self.ignoreSpaces(p.name, 'http://boinc.bakerlab.org/rosetta/')
        self.ignoreSpaces(p.name_short, 'boinc.bakerlab/rosetta')
        self.ignoreSpaces(str(p.statistics), """Total credit,  user: 2 543, host: 2 543, 100%
        Avg credit, user: 227, host: 227, 100%""")

    def test_worldcommunitygrid(self):
        p = parse.boinccmd.project(parse_input.project_worldcommunitygrid)
        print p
        self.ignoreSpaces(p.name, 'http://www.worldcommunitygrid.org/')
        self.ignoreSpaces(p.name_short, 'worldcommunitygrid')
        self.ignoreSpaces(str(p.statistics), """Total credit,  user: 213 009, host: 207 378, 97%
        Avg credit, user: 1 770, host: 1 769, 100%""")

    def test_app(self):
        p = parse.boinccmd.application("""<app>
    <name>hcc1</name>
    <user_friendly_name>Help Conquer Cancer</user_friendly_name>
    <non_cpu_intensive>0</non_cpu_intensive>
    </app>""")
        print p
    
    def test_task(self):
        p = parse.boinccmd.task(parse_input.task_active)
        print p
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApplication)
    unittest.TextTestRunner(verbosity=2).run(suite)
