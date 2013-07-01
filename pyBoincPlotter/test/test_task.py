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
    
    def test_xml(self):
        self.t = task.Task_local.createFromXML("""<result> 
<name>faah41856_ZINC09836600_xBr27_refmac2_A_PR_02_0</name>
<wu_name>faah41856_ZINC09836600_xBr27_refmac2_A_PR_02</wu_name>
<version_num>715</version_num> 
<plan_class></plan_class>
<project_url>http://www.worldcommunitygrid.org/</project_url>
<final_cpu_time>0.000000</final_cpu_time>
<final_elapsed_time>0.000000</final_elapsed_time>
<exit_status>0</exit_status> 
<state>2</state> 
<report_deadline>1373310023.000000</report_deadline> 
<received_time>1372446024.959453</received_time> 
<estimated_cpu_time_remaining>28329.146516</estimated_cpu_time_remaining>""")
        self.assertEqual(self.t.state_str, 'ready to run')

    def test_xml2(self):
        self.t = task.Task_local.createFromXML("""<result>
<name>DSFL_00100-37_0000046_0555_1</name>
<wu_name>DSFL_00100-37_0000046_0555</wu_name>
<version_num>625</version_num>
<plan_class></plan_class>
<project_url>http://www.worldcommunitygrid.org/</project_url>
<final_cpu_time>0.000000</final_cpu_time>
<final_elapsed_time>0.000000</final_elapsed_time>
<exit_status>0</exit_status>
<state>2</state>
<report_deadline>1373310023.000000</report_deadline>
<received_time>1372446024.959453</received_time>
<estimated_cpu_time_remaining>2060.234200</estimated_cpu_time_remaining>
<active_task>
<active_task_state>1</active_task_state>
<app_version_num>625</app_version_num>
<slot>5</slot>
<pid>7130</pid>
<scheduler_state>2</scheduler_state>
<checkpoint_cpu_time>11916.430000</checkpoint_cpu_time>
<fraction_done>0.883333</fraction_done>
<current_cpu_time>12429.430000</current_cpu_time>
<elapsed_time>12566.508714</elapsed_time>
<swap_size>2591920128.000000</swap_size>
<working_set_size>54267904.000000</working_set_size>
<working_set_size_smoothed>54262111.801669</working_set_size_smoothed>
<page_fault_rate>0.000000</page_fault_rate>
<graphics_exec_path>/Library/Application Support/BOINC Data/projects/www.worldcommunitygrid.org/wcgrid_dsfl_gfx_prod_darwin_64.x86.6.25</graphics_exec_path>
<slot_path>/Library/Application Support/BOINC Data/slots/5</slot_path>
</active_task>""")
        self.assertEqual(self.t.state_str, 'running')

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
