
class Task(object):
    desc_state = ['downloading', 'ready to run', 'running', 'suspended', 'paused', 'computation completed', 'uploading', 'ready to report', 'unknown']

    def __init__(self, name='', device='localhost',
                 state='unknown', fractionDone='0',
                 elapsedCPUtime=None, remainingCPUtime=None, deadline=None,
                 claimedCredit=None, grantedCredit=None):
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

        self.grantedCredit = grantedCredit # stored as float
        self.claimedCredit = claimedCredit # stored as float

    # Conversion functions
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

    @property
    def nameShort(self):
        if len(self.name) > 15:
            return self.name[:15] + '...'
        else:
            return self.name        

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
        if self.done(): self._fractionDone = 100
        return "{:.0f} %".format(self._fractionDone)
    @fractionDone.setter
    def fractionDone(self, fractionDone):
        self._fractionDone = float(fractionDone)*100

class Task_local(Task):
    def __init__(self, schedularState, active, **kwargs):
        self.schedularState = schedularState
        self.active = active
        Task.__init__(self, **kwargs)

    def done(self):
        return self.remainingCPUtime == '0:00:00'
        
    @Task.property
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
