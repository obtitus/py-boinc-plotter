# Standard python imports
import unittest

# This project
import tasks

class TestTasks_local(unittest.TestCase):   
    def setUp(self, schedularState='0', active='0', name='foobar 123451234512345', device='this',
              state='0', fractionDone='0',
              elapsedCPUtime='60', remainingCPUtime='3600', deadline='Tue Jun 25 10:41:00 2013'):

        self.t = tasks.Task_local(schedularState=schedularState, active=active, name=name, device=device,
                                  state=state, fractionDone=fractionDone,
                                  elapsedCPUtime=elapsedCPUtime, remainingCPUtime=remainingCPUtime, deadline=deadline)

    def test_name(self):
        self.assertEqual(self.t.name, 'foobar 123451234512345')
        self.assertEqual(self.t.nameShort, 'foobar 12345123...')

    def test_device(self):
        self.assertEqual(self.t.device, 'this')
    
    def test_state(self):
        self.assertEqual(self.t._schedularState, 0)
        self.assertEqual(self.t._active, 0)
        self.assertEqual(self.t._state, 0)
        self.assertEqual(self.t.state, 'ready to run')

    def test_states(self):
        def test(wanted, **kwargs):
            self.setUp(**kwargs)
            self.assertEqual(self.t.state, wanted)
        test('ready to run', state='2', schedularState='0', active='0')
        test('ready to run', state='4', schedularState='0', active='0')
        test('suspended', state='2', schedularState='1', active='9')
        # TODO: add more

    def test_fractionDone(self):
        def test(wanted, **kwargs):
            self.setUp(**kwargs)
            self.assertEqual(self.t.fractionDone, wanted)

        test('0 %')
        test('100 %', remainingCPUtime='0')

    def test_elapsedCPUtime(self):
        self.assertEqual(self.t.elapsedCPUtime, '0:01:00')
    
    def test_remainingCPUtime(self):
        self.assertEqual(self.t.remainingCPUtime, '1:00:00')
    
    # def test_deadline(self):
    #     now = datetime.datetime.today()
    #     delta = datetime.strptime('Tue Jun 25 10:41:00 2013', '%a %b %d %H:%M:%S %Y') - now
        

class TestTasks_web(TestTasks_local):
    def setUp(self, claimedCredit='0', grantedCredit='0',
              name='foobar 123451234512345', device='this',
              state='in progress', fractionDone='0',
              elapsedCPUtime='60', remainingCPUtime='3600', deadline='25 Jun 2013 10:41:00 UTC'):

        self.t = tasks.Task_web(claimedCredit=claimedCredit, grantedCredit=grantedCredit,
                                name=name, device=device,
                                state=state, fractionDone=fractionDone,
                                elapsedCPUtime=elapsedCPUtime, remainingCPUtime=remainingCPUtime, deadline=deadline)

    def test_state(self):
        self.assertEqual(self.t._state, 9)
        self.assertEqual(self.t.state, 'in progress')

    def test_states(self):
        def test(wanted, **kwargs):
            self.setUp(**kwargs)
            self.assertEqual(self.t.state, wanted)
        test('valid', state='Completed and validated')

    def test_fractionDone(self):
        def test(wanted, **kwargs):
            self.setUp(**kwargs)
            self.assertEqual(self.t.fractionDone, wanted)

        test('0 %')
        test('100 %', state='completed and validated')

if __name__ == '__main__':
    for t in [TestTasks_local, TestTasks_web]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        unittest.TextTestRunner(verbosity=2).run(suite)
