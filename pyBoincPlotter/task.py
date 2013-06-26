"""
Task -> Task_local
Task -> Task_web -> Task_web_worlcommunitygrid
"""

# Standard python imports
import datetime
# non standard:
from bs4 import BeautifulSoup

class Task(object):
    """
    Mostly handles string conversion around the following properties:
    - name
    - device
    - state
    - elapsedCPUtime
    - remainingCPUtime
    - deadline
    - claimedCredit
    - grantedCredit
    Subclasses Task_local and Task_web are the one to use depending on source.
    """
    desc_state = ['downloading', 'ready to run', 'running', 'suspended', 'paused', 'computation completed', 'uploading', 'ready to report', 'unknown']
    fmt = '{0:<{col0}} {1:<{col1}} {2:<{col2}} {3:<{col3}} {4:<{col4}} {5:<{col5}} {6:<{col6}} {6:<{col6}} {7:<{col7}} {8:<{col8}}'
    columnSpacing = dict()
    for i in range(0, 8+1):
        columnSpacing['col'+str(i)] = 0

    def __init__(self, name='', device='localhost',
                 state='unknown', fractionDone='0',
                 elapsedCPUtime=None, remainingCPUtime=None, deadline=None):
        """
        Each attribute has a string representation and a 'data' representation:
        Use self.set_fractionDone(str) for the string to object conversion.
        type(self.fractionDone_str) == str
        type(self.fractionDone) == float
        each attribute has a setter method that assumes a string is passed in. This is then converted to a python object
        like float, datetime or timedelta.
        """
        self.setName(name)                # There is also a self.name_short which is max 15 characters long
        self.setDevice(device)

        self.setState(state) # Stored as integer representing index in the self.desc_state list
        self.setFractionDone(fractionDone) # stored as float

        self.setElapsedCPUtime(elapsedCPUtime) # stored as timedelta, see strToTimedelta and timedeltaToStr
        self.setRemainingCPUtime(remainingCPUtime) # stored as timedelta, see strToTimedelta and timedeltaToStr
        self.setDeadline(deadline)                 # stored as datetime, string is time until deadline

    def __str__(self):
        return self.fmt.format(self.nameShort_str,
                               self.state_str, self.fractionDone_str,
                               self.elapsedCPUtime_str, self.remainingCPUtime_str, self.deadline_str, 
                               self.claimedCredit_str, self.grantedCredit_str, self.device_str, **self.columnSpacing)
    
    #
    # Conversion functions
    #
    # Applied to self.elapsedCPUtime and self.remainingCPUtime
    def strToTimedelta(self, sec):
        timedelta = datetime.timedelta(seconds=float(sec))
        return timedelta

    def timedeltaToStr(self, timedelta):
        timedelta = str(timedelta)
        ix = timedelta.find('.')
        if ix != -1:
            timedelta = timedelta[:ix]
        return timedelta

    #
    # Setters and <>_str
    #
    @property
    def nameShort_str(self):
        if len(self.name) > 15:
            return self.name[:15] + '...'
        else:
            return self.name

    def setDevicce(self, device):
        self.device = device

    @property
    def state_str(self):
        state = self.desc_state[self.state]
        return state

    def setState(self, state):
        try:
            self.state = int(state)
        except ValueError: # lets hope its a string representing the state
            try:
                self.state = self.desc_state.index(state.lower())
            except:                     # guess not
                self.desc_state.append(state.lower()) # now it is!
                self.state = self.desc_state.index(state.lower())

    @property
    def fractionDone_str(self):
        if self.done():
            self.fractionDone = 100
        return "{:.0f} %".format(self.fractionDone)

    def setFractionDone(self, fractionDone):
        self.fractionDone = float(fractionDone)*100

    @property
    def elapsedCPUtime_str(self):
        return self.timedeltaToStr(self.elapsedCPUtime)

    def setElapsedCPUtime(self, elapsedCPUtime):
        self.elapsedCPUtime = self.strToTimedelta(elapsedCPUtime)

    @property
    def remainingCPUtime(self):
        return self.timedeltaToStr(self.remainingCPUtime)

    def setRemainingCPUtime(self, remainingCPUtime):
        self.remainingCPUtime = self.strToTimedelta(remainingCPUtime)

    @property
    def deadline(self):
        """ Time until deadline
        """
        now = datetime.datetime.today()
        delta = self.deadline - now
        s = self.timedeltaToStr(delta)
        if delta.days < 0:
            delta = now - self.deadline
            s = '-' + self.timedeltaToStr(delta)
        return s

    def setDeadline(self, deadline):
        """ Store deadline as datetime object
        """
        self.deadline = datetime.datetime.strptime(deadline, self.fmt_date)

class Task_local(Task):
    desc_schedularState = ['ready to start', 'suspended', 'running']
    desc_active = ['paused', 'running', 2, 3, 4, 5, 6, 7, 8, 'running']
    def __init__(self, schedularState, active, **kwargs):
        self.setSchedularState(schedularState)
        self.setActive(active)
        Task.__init__(self, **kwargs)

    @staticmethod
    def createFromXML(xml):
        """
        Expects the result block:
        <result>
        ...
        </result>
        from the boinc rpc
        """
        soup = BeautifulSoup(xml, "xml")
        return Task_local(name=soup.wu_name.text,
                          state=soup.state.text,
                          fractionDone=soup.fraction_done.text,
                          elapsedCPUtime=soup.elapsed_time.text,
                          remainingCPUtime=soup.estimated_cpu_time_remaining.text,
                          deadline=soup.report_deadline.text,
                          schedularState=soup.scheduler_state.text,
                          active=soup.active_task_state.text)

    def done(self):
        return self.remainingCPUtime == '0:00:00'

    def setDeadline(self, deadline):
        self.deadline = datetime.datetime.fromtimestamp(float(deadline))

    @Task.state_str.getter
    def state_str(self):
        state = self.desc_state[self.state]
        # Hack
        # The current state seems to be determined by 3 numbers: state, active and schedularState.
        # I have been unable to determine their exact meaning, so the following is based on comparision with the boincManager.
        if self.done(): # done
            self.currentCPUtime = self.finalCPUtime
            state = 'ready to report'
        elif state == 'computation completed':
            state = 'completed'
        elif self.schedularState == 'suspended':
            state = self.schedularState
        elif self.schedularState == 'ready to start':
            state = 'ready to run'
        elif self.active in ['Paused', 'Running']:
            state = self.active
        return state

    @property
    def schedularState_str(self):
        state = self.desc_schedularState[self.schedularState]
        return state

    def setSchedularState(self, state):
        self.schedularState = int(state)

    @property
    def active_str(self):
        state = self.desc_active[self.active]
        return state

    def setActive(self, state):
        self.active = int(state)

class Task_web(Task):
    fmt_date = '%d %b %Y %H:%M:%S UTC'

    def __init__(self, claimedCredit='0', grantedCredit='0', **kwargs):
        self.setGrantedCredit(grantedCredit) # stored as float
        self.setClaimedCredit(claimedCredit) # stored as float
        super(Task_web, self).__init__(**kwargs)

    def toFloat(self, value):
        value = value.replace(',', '')
        value = value.replace('---', '0')
        return float(value)

    def done(self):
        return not(self.desc_state[self.state] == 'in progress')

    @property
    def grantedCredit_str(self):
        return str(self.grantedCredit)

    def setGrantedCredit(self, grantedCredit):
        self.grantedCredit = self.toFloat(grantedCredit)

    @property
    def claimedCredit(self):
        return str(self.claimedCredit)

    def setClaimedCredit(self, claimedCredit):
        self.claimedCredit = self.toFloat(claimedCredit)

    def setState(self, state):
        if state.lower() == 'completed and validated':
            state = 'valid'
        elif state.lower() == 'over success done':
            state = 'valid'
        elif state.lower().endswith('waiting for validation'):
            state = 'pending validation'
        elif state.lower().endswith('validation inconclusive'):
            state = 'inconclusive'
        elif state.lower().endswith('invalid'):
            state = 'invalid'
        elif state.lower().startswith('in progress'):
            state = 'in progress'
        if 'error' in state.lower():
            state = 'error'

        super(self._class__, self).setState(self, state)

class Task_web_worlcommunitygrid(Task_web):
    fmt_date = '%m/%d/%y %H:%M:%S'

class Task_jobLog(Task):
    """
    Represents a task from the job_log, with the following fields:
        ue - estimated_runtime_uncorrected
        ct - final_cpu_time, cpu time to finish
        fe - rsc_fpops_est, estimated flops
        et - final_elapsed_time, clock time to finish    
    """
    def __init__(self, time, name, 
                 ue, ct, fe, et):
        super(__class__, self).__init__(name=name, fractionDone='100',
                                        elapsedCPUtime=ct, remainingCPUtime='0')
        self.setTime(time)
        # Lets just keep it simple, float already has a sane str() version and matplotlib won't mind if these are strings
        self.estimated_runtime_uncorrected = float(ue)
        self.rsc_fpops_est = float(fe)
        self.final_elapsed_time = float(et)

    @staticmethod
    def createFromJobLog(line):
        """
        Expects a single line from the job log file
        """
        s = line.split()
        assert len(s) == 11, 'Line in job log not recognized {0} "{1}" -> "{2}"'.format(len(s), line, s)
        return Task_jobLog(time=s[0], name=s[8],
                           ue=s[2], ct=s[4], fe=s[6], et=s[10])

    def setTime(self, value):
        t = int(s[0])
        self.time = datetime.datetime.fromtimestamp(t)
