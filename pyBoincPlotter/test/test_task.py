
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
# Standard python imports
import unittest
import datetime

# This project
import task
import parse_input

class TestTask(unittest.TestCase):
    def setUp(self):
        pass

    def test_str(self):
        print ''
        t1 = task.Task(name='Task object')
        print t1
        t2 = task.Task_local(name='Task local object')
        print t2
        t3 = task.Task_web(name='Task web object')
        print t3
        t4 = task.Task_web_worldcommunitygrid(name='Task web worldcommunitygrid object')
        print t4
        l = [t1, t2, t3, t4]
        task.adjustColumnSpacing(l)
        for t in l:
            print t

class TestTask_local(unittest.TestCase):
    def setUp(self, schedularState='0', active='0', name='foobar 123451234512345', device='this',
              state='0', fractionDone='0',
              elapsedCPUtime='60', remainingCPUtime='3600', deadline='1372752295.000000',
              memUsage='311340577.134'):

        self.t = task.Task_local(schedularState=schedularState, active=active, name=name, device=device,
                                 state=state, fractionDone=fractionDone,
                                 elapsedCPUtime=elapsedCPUtime, remainingCPUtime=remainingCPUtime, deadline=deadline,
                                 memUsage=memUsage)

    def test_name(self):
        self.assertEqual(self.t.name, 'foobar123451234512345')
        self.assertEqual(self.t.nameShort_str, 'foobar123451234...')

    def test_device(self):
        self.assertEqual(self.t.device_str, 'this')
    
    def test_state(self):
        self.assertEqual(self.t.schedularState, 0)
        self.assertEqual(self.t.active, 0)
        self.assertEqual(self.t.state, 0)
        self.assertEqual(self.t.state_str, 'ready to run')

    def test_states(self):
        def test(wanted, **kwargs):
            self.setUp(**kwargs)
            self.assertEqual(self.t.state_str, wanted)
        test('ready to run', state='2', schedularState='0', active='0')
        test('ready to run', state='4', schedularState='0', active='0')
        test('suspended', state='2', schedularState='1', active='9')

    def test_fractionDone(self):
        def test(wanted, **kwargs):
            self.setUp(**kwargs)
            self.assertEqual(self.t.fractionDone_str, wanted)

        test('0 %')
        test('100 %', remainingCPUtime='0')

    def test_elapsedCPUtime(self):
        self.assertEqual(self.t.elapsedCPUtime_str, '0:01:00')
    
    def test_remainingCPUtime(self):
        self.assertEqual(self.t.remainingCPUtime_str, '1:00:00')
    
    def test_deadline(self):
        self.assertEqual(self.t.deadline, datetime.datetime(2013, 7, 2, 10, 4, 55))
    
    def test_memUsage(self):
        self.assertEqual(self.t.memUsage, 311340577.134)
        self.assertEqual(self.t.memUsage_str, '311 MB')
        
        self.setUp(memUsage='3000000000')
        self.assertEqual(self.t.memUsage_str, '3 GB')
    
    def test_xml(self):
        self.t = task.Task_local.createFromXML(parse_input.workunit_ready_to_run)
        self.assertEqual(self.t.state_str, 'ready to run')
        self.assertEqual(self.t.pendingTime(), (28329.146516, 0, 0))

    def test_xml2(self):
        self.t = task.Task_local.createFromXML(parse_input.workunit_running)
        self.assertEqual(self.t.state_str, 'running')
        self.assertEqual(self.t.pendingTime(), (0, 14626.742914, 0))

    def test_xml3(self):
        self.t = task.Task_local.createFromXML(parse_input.workunit_suspended)
        self.assertEqual(self.t.state_str, 'suspended')
        self.assertEqual(self.t.pendingTime(), (0, 384436.545728, 0))

class TestTask_web(TestTask_local):
    def setUp(self, claimedCredit='0', grantedCredit='0',
              name='foobar 123451234512345', device='this',
              state='in progress', fractionDone='0',
              elapsedCPUtime='60', remainingCPUtime='3600', deadline='2 Jul 2013 10:04:55 UTC'):

        self.t = task.Task_web(claimedCredit=claimedCredit, grantedCredit=grantedCredit,
                                name=name, device=device,
                                state=state, fractionDone=fractionDone,
                                elapsedCPUtime=elapsedCPUtime, remainingCPUtime=remainingCPUtime, deadline=deadline)

    def test_xml(self):         # overrride
        pass
    def test_xml2(self):         # overrride
        pass
    def test_xml3(self):         # overrride
        pass
    def test_memUsage(self):
        pass

    def test_state(self):
        self.assertEqual(self.t.state, 9)
        self.assertEqual(self.t.state_str, 'in progress')

    def test_states(self):
        def test(wanted, **kwargs):
            self.setUp(**kwargs)
            self.assertEqual(self.t.state_str, wanted)
        test('valid', state='Completed and validated')

    def test_fractionDone(self):
        def test(wanted, **kwargs):
            self.setUp(**kwargs)
            self.assertEqual(self.t.fractionDone_str, wanted)

        test('0 %')
        test('100 %', state='completed and validated')

if __name__ == '__main__':
    for t in [TestTask, TestTask_local, TestTask_web]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        unittest.TextTestRunner(verbosity=2).run(suite)
