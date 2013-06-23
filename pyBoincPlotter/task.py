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
        type(self.fractionDone) == str
        type(self._fractionDone) == float
        each attribute has a setter method that assumes a string is passed in. This is then converted to a python object
        like float, datetime or timedelta.
        """
        self.name = name                # There is also a self.name_short which is max 15 characters long
        self.device = device

        self.state = state # Stored as integer representing index in the self.desc_state list
        self.fractionDone = fractionDone # stored as float

        self.elapsedCPUtime = elapsedCPUtime # stored as timedelta, see strToTimedelta and timedeltaToStr
        self.remainingCPUtime = remainingCPUtime # stored as timedelta, see strToTimedelta and timedeltaToStr
        self.deadline = deadline                 # stored as datetime, string is time until deadline

    def __str__(self):
        return self.fmt.format(self.nameShort,
                               self.state, self.fractionDone,
                               self.elapsedCPUtime, self.remainingCPUtime, self.deadline, 
                               self.claimedCredit, self.grantedCredit, self.device, **self.columnSpacing)
    
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
    # Properties
    #
    @property
    def nameShort(self):
        if len(self.name) > 15:
            return self.name[:15] + '...'
        else:
            return self.name

    # device - not needed

    @property
    def state(self):
        state = self.desc_state[self._state]
        return state
    @state.setter
    def state(self, state):
        try:
            self._state = int(state)
        except ValueError: # lets hope its a string representing the state
            try:
                self._state = self.desc_state.index(state.lower())
            except:                     # guess not
                self.desc_state.append(state.lower()) # now it is!
                self._state = self.desc_state.index(state.lower())

    @property
    def fractionDone(self):
        if self.done():
            self._fractionDone = 100
        return "{:.0f} %".format(self._fractionDone)
    @fractionDone.setter
    def fractionDone(self, fractionDone):
        self._fractionDone = float(fractionDone)*100

    @property
    def elapsedCPUtime(self):
        return self.timedeltaToStr(self._elapsedCPUtime)
    @elapsedCPUtime.setter
    def elapsedCPUtime(self, elapsedCPUtime):
        self._elapsedCPUtime = self.strToTimedelta(elapsedCPUtime)

    @property
    def remainingCPUtime(self):
        return self.timedeltaToStr(self._remainingCPUtime)
    @remainingCPUtime.setter
    def remainingCPUtime(self, remainingCPUtime):
        self._remainingCPUtime = self.strToTimedelta(remainingCPUtime)

    @property
    def deadline(self):
        """ Time until deadline
        """
        now = datetime.datetime.today()
        delta = self._deadline - now
        s = self.timedeltaToStr(delta)
        if delta.days < 0:
            delta = now - self._deadline
            s = '-' + self.timedeltaToStr(delta)
        return s
    @deadline.setter
    def deadline(self, deadline):
        """ Store deadline as datetime object
        """
        self._deadline = datetime.datetime.strptime(deadline, self.fmt_date)

class Task_local(Task):
    desc_schedularState = ['ready to start', 'suspended', 'running']
    desc_active = ['paused', 'running', 2, 3, 4, 5, 6, 7, 8, 'running']
    def __init__(self, schedularState, active, **kwargs):
        self.schedularState = schedularState
        self.active = active
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

    @Task.deadline.setter
    def deadline(self, deadline):
        self._deadline = datetime.datetime.fromtimestamp(float(deadline))

    @Task.state.getter
    def state(self):
        state = self.desc_state[self._state]
        # Hack
        # The current state seems to be determined by 3 numbers: state, active and schedularState.
        # I have been unable to determine their exact meaning, so the following is based on comparision with the boincManager.
        if self.done(): # done
            self._currentCPUtime = self._finalCPUtime
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
    def schedularState(self):
        state = self.desc_schedularState[self._schedularState]
        return state
    @schedularState.setter
    def schedularState(self, state):
        self._schedularState = int(state)


    @property
    def active(self):
        state = self.desc_active[self._active]
        return state
    @active.setter
    def active(self, state):
        self._active = int(state)

class Task_web(Task):
    fmt_date = '%d %b %Y %H:%M:%S UTC'

    def __init__(self, claimedCredit='0', grantedCredit='0', **kwargs):
        self.grantedCredit = grantedCredit # stored as float
        self.claimedCredit = claimedCredit # stored as float
        super(Task_web, self).__init__(**kwargs)

    def toFloat(self, value):
        value = value.replace(',', '')
        value = value.replace('---', '0')
        return float(value)

    def done(self):
        return not(self.desc_state[self._state] == 'in progress')

    @property
    def grantedCredit(self):
        return str(self._grantedCredit)
    @grantedCredit.setter
    def grantedCredit(self, grantedCredit):
        self._grantedCredit = self.toFloat(grantedCredit)

    @property
    def claimedCredit(self):
        return str(self._claimedCredit)
    @claimedCredit.setter
    def claimedCredit(self, claimedCredit):
        self._claimedCredit = self.toFloat(claimedCredit)

    @Task.state.setter
    def state(self, state):
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

        super(Task_web, self.__class__).state.fset(self, state)

class Task_web_worlcommunitygrid(Task_web):
    fmt_date = '%m/%d/%y %H:%M:%S'
