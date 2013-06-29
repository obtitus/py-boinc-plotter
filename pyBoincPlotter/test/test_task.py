# Standard python imports
import unittest
import datetime

# This project
import task

class TestTask_local(unittest.TestCase):   
    def setUp(self, schedularState='0', active='0', name='foobar 123451234512345', device='this',
              state='0', fractionDone='0',
              elapsedCPUtime='60', remainingCPUtime='3600', deadline='1372752295.000000'):

        self.t = task.Task_local(schedularState=schedularState, active=active, name=name, device=device,
                                  state=state, fractionDone=fractionDone,
                                  elapsedCPUtime=elapsedCPUtime, remainingCPUtime=remainingCPUtime, deadline=deadline)

    def test_name(self):
        self.assertEqual(self.t.name, 'foobar 123451234512345')
        self.assertEqual(self.t.nameShort_str, 'foobar 12345123...')

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
        # TODO: add more

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

class TestTask_web(TestTask_local):
    def setUp(self, claimedCredit='0', grantedCredit='0',
              name='foobar 123451234512345', device='this',
              state='in progress', fractionDone='0',
              elapsedCPUtime='60', remainingCPUtime='3600', deadline='2 Jul 2013 10:04:55 UTC'):

        self.t = task.Task_web(claimedCredit=claimedCredit, grantedCredit=grantedCredit,
                                name=name, device=device,
                                state=state, fractionDone=fractionDone,
                                elapsedCPUtime=elapsedCPUtime, remainingCPUtime=remainingCPUtime, deadline=deadline)

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
    for t in [TestTask_local, TestTask_web]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        unittest.TextTestRunner(verbosity=2).run(suite)
