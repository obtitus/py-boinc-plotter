
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
"""
Task -> Task_local
Task -> Task_web -> Task_web_worlcommunitygrid
"""

# Standard python imports
import datetime
import logging
logger = logging.getLogger('boinc.task')

# non standard:
from bs4 import BeautifulSoup

# This project
import util

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
    fmt_date = '%d %b %Y %H:%M:%S UTC'
    def __init__(self, name='', device='localhost',
                 state='unknown', fractionDone='0',
                 checkpointCPUtime=None, currentCPUtime=None,
                 elapsedCPUtime='0', remainingCPUtime='0', deadline=None):
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
        self.setCheckpoint(checkpointCPUtime, currentCPUtime)
        self.setDeadline(deadline)                 # stored as datetime, string is time until deadline

    N = 10
    fmt = []
    columnSpacing = dict()
    for i in range(N):
        columnSpacing['col%d' % i] = 0
        fmt.append('{%d:>{col%d}}' % (i, i))
    fmt = " ".join(fmt)

    def toString(self):
        return [self.nameShort_str,
                self.state_str, self.fractionDone_str,
                self.elapsedCPUtime_str, self.remainingCPUtime_str, self.deadline_str, 
                self.device_str]
    
    def __str__(self):
        s = self.toString()
        for i in range(Task.N - len(s)):
            s.append('')

        return Task.fmt.format(*s, **self.columnSpacing)
    
    def done(self):
        return not(self.desc_state[self.state] == 'in progress')

    #
    # Conversion functions
    #
    # Applied to self.elapsedCPUtime and self.remainingCPUtime
    def strToTimedelta(self, sec):
        timedelta = datetime.timedelta(seconds=self.toFloat(sec))
        return timedelta

    def timedeltaToStr(self, timedelta):
        timedelta = str(timedelta)
        ix = timedelta.find('.')
        if ix != -1:
            timedelta = timedelta[:ix]
        return timedelta

    def toFloat(self, value):
        try:
            value = value.replace(',', '')
        except:                 # guess its not a string
            pass
        # if value == '---':
        #     value = '0'
        try:
            return float(value)
        except ValueError:
            return 0

    #
    # Setters and <>_str
    #
    @property
    def nameShort_str(self):
        if len(self.name) > 15:
            return self.name[:15] + '...'
        else:
            return self.name
    
    def setName(self, value):
        self.name = value.replace(' ', '')

    @property
    def device_str(self):
        return self.device

    def setDevice(self, device):
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
                logger.debug('Adding state %s', state.lower())
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
        elapsed = self.timedeltaToStr(self.elapsedCPUtime)
        # if self.checkpoint != None:
        #     elapsed += " ({})".format(self.checkpoint_str)
        return elapsed

    def setElapsedCPUtime(self, elapsedCPUtime):
        if elapsedCPUtime == '---':
            elapsedCPUtime = '0'
        self.elapsedCPUtime = self.strToTimedelta(elapsedCPUtime)

    @property
    def remainingCPUtime_str(self):
        return self.timedeltaToStr(self.remainingCPUtime)

    def setRemainingCPUtime(self, remainingCPUtime):
        self.__state = None
        self.remainingCPUtime = self.strToTimedelta(remainingCPUtime)

    # @property
    # def checkpoint_str(self):
    #     return self.timedeltaToStr(self.checkpoint)

    def setCheckpoint(self, checkpointCPUtime, currentCPUtime):
        self.checkpoint = None
        if checkpointCPUtime != None and currentCPUtime != None:
            try:
                sec = self.toFloat(currentCPUtime) - self.toFloat(checkpointCPUtime)
                if sec < 0:     # negative timedeltas are wierd
                    self.checkpoint = datetime.timedelta(seconds=-sec)
                    self.checkpoint_str = '-' + self.timedeltaToStr(self.checkpoint)
                else:
                    self.checkpoint = datetime.timedelta(seconds=sec)
                    self.checkpoint_str = self.timedeltaToStr(self.checkpoint)
            except:
                pass

    @property
    def deadline_str(self):
        """ Time until deadline
        """
        if self.deadline is not None:
            now = datetime.datetime.today()
            delta = self.deadline - now
            s = self.timedeltaToStr(delta)
            if delta.days < 0:
                delta = now - self.deadline
                s = '-' + self.timedeltaToStr(delta)
        else:
            return '-'
        return s

    def setDeadline(self, deadline):
        """ Store deadline as datetime object
        """
        if deadline is not None:
            deadline = deadline.replace('|', '')
            deadline = deadline.replace(',', '')
            self.deadline = datetime.datetime.strptime(deadline, self.fmt_date)
        else:
            self.deadline = None

class Task_local(Task):
    desc_schedularState = ['ready to start', 'suspended', 'running', 'unknown']
    # Based on common_defs.h
    desc_active = ['paused', 'running',                      # 0, 1
                   'exited', 'was signaled', 'exit unknown', # 2, 3, 4
                   'abort pending', 'aborted', 'unable to start', # 5, 6, 7
                   'waiting to quit', 'suspended', 'waiting for copy', # 8, 9, 10
                   'unknown']   # -1
    def __init__(self, schedularState=-1, active=-1, memUsage=0, resources='', **kwargs):
        self.__state = None      # cache

        self.setSchedularState(schedularState)
        self.setActive(active)
        self.memUsage = float(memUsage)
        self.resources = resources
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
        try:
            soup = BeautifulSoup(xml, "xml")
            kwargs = dict(name = soup.wu_name,
                          state = soup.state or -1,
                          fractionDone = soup.fraction_done or 0,
                          elapsedCPUtime = soup.elapsed_time or soup.final_elapsed_time or 0,
                          remainingCPUtime = soup.estimated_cpu_time_remaining or 0,
                          checkpointCPUtime = soup.checkpoint_cpu_time or None,
                          currentCPUtime = soup.current_cpu_time or None,
                          deadline = soup.report_deadline,
                          schedularState = soup.schedular_state or -1,
                          active = soup.active_task_state or -1,
                          memUsage = soup.working_set_size_smoothed or 0,
                          resources = soup.resources or '')

            for key in kwargs:
                try:
                    kwargs[key] = kwargs[key].text # ok if soup stuff
                except AttributeError:
                    pass
            
            return Task_local(**kwargs)
        except Exception as e:
            logger.exception('Trying to create task out of {}, got'.format(xml))

    def done(self):
        return self.remainingCPUtime_str == '0:00:00'

    def toString(self):
        s = super(Task_local, self).toString()
        s.extend([self.memUsage_str, self.resources])
        return s

    @property
    def memUsage_str(self):
        if self.memUsage == 0:
            return ''
        else:
            return util.fmtSi(self.memUsage) + 'B'
            # mem = self.memUsage/1e6
            # suffix = 'MB'
            # if mem > 1000:
            #     mem /= 1e3
            #     suffix = 'GB'
            # return '{:.3g} {}'.format(mem, suffix)

    def setDeadline(self, deadline):
        if deadline is not None:
            self.deadline = datetime.datetime.fromtimestamp(float(deadline))
        else:
            self.deadline = None

    @Task.state_str.getter
    def state_str(self):
        if self.__state is None:
            state = self.desc_state[self.state]
            # Hack
            # The current state seems to be determined by 3 numbers: state, active and schedularState.
            # I have been unable to determine their exact meaning, so the following is based on comparision with the boincManager.
            if self.done(): # done
                #self.currentCPUtime = self.finalCPUtime
                state = 'ready to report'
            elif self.state == 2 and self.active == 0: # Shows up as 'Waiting to run'
                state = 'suspended'
            elif self.schedularState == -1 and self.active == -1: # Very strange hack
                state = 'ready to run'
            elif state == 'computation completed':
                state = 'completed'
            elif self.schedularState_str == 'suspended':
                state = self.schedularState_str
            elif self.schedularState_str == 'ready to start':
                state = 'ready to run'
            elif self.active in (2, 9):
                state = self.active_str
            logger.debug('infered state %s, flags %s %s %s', state, 
                         self.state, self.schedularState, self.active)
            self.__state = state
        else:
            state = self.__state

        return state

    @property
    def schedularState_str(self):
        state = self.desc_schedularState[self.schedularState]
        return state

    def setSchedularState(self, state):
        self.__state = None
        self.schedularState = int(state)

    @property
    def active_str(self):
        state = self.desc_active[self.active]
        return state

    def setActive(self, state):
        self.__state = None
        self.active = int(state)

    def pendingTime(self, include_elapsedCPUtime=True):
        """Returns seconds for pending, started
        and task waiting for validation.
        """
        def getSeconds(task):
            ret = task.remainingCPUtime
            if include_elapsedCPUtime:
                ret += task.elapsedCPUtime
            return ret.total_seconds()

        logger.debug('pendingTime, task = %s', self)
        if self.done():
            logger.debug('adding to validation')
            return (0, 0, getSeconds(self))
        elif self.elapsedCPUtime != datetime.timedelta(0):
            logger.debug('adding to running')
            return (0, getSeconds(self), 0)
        else:
            logger.debug('adding to pending')
            return (getSeconds(self), 0, 0)

class Task_fileTransfer(Task):
    def __init__(self, project_url, project_name, name, nbytes, 
                 status, time_so_far, nbytes_xferred, is_upload):
        kwargs = dict()
        if is_upload == '1':
            state = 'uploading'
        else:                   # todo: fix, use status as well
            state = 'downloading'
        nbytes = float(nbytes)
        nbytes_xferred = float(nbytes_xferred)

        kwargs['elapsedCPUtime'] = time_so_far
        kwargs['name'] = name
        kwargs['state'] = state
        if nbytes != 0:
            kwargs['fractionDone'] = 1 - (nbytes - nbytes_xferred)/nbytes
        self.bytesDone = '{}B/{}B'.format(util.fmtSi(nbytes_xferred), 
                                        util.fmtSi(nbytes))
        self.project_url = project_url
        self.project_name = project_name
        Task.__init__(self, **kwargs)

    def done(self):
        return False            # override superclass since it does a few wierd things with the fractionDone

    def toString(self):
        s = super(Task_fileTransfer, self).toString()
        s[5] = self.bytesDone
        return s

    @staticmethod
    def createFromXML(xml):
        """
        Expects the result block:
        <file_transfer>
        ...
        </file_transfer>
        from the boinc rpc
        """
        try:
            soup = BeautifulSoup(xml, "xml")
            kwargs = dict(project_url = soup.project_url or '',
                          project_name = soup.project_name or '',
                          name = soup.find('name') or '',   # Vops: soup.name is 'reserved' so need to use find('name')
                          nbytes = soup.nbytes or 0,
                          status = soup.status or None,
                          time_so_far = soup.time_so_far or 0,
                          nbytes_xferred = soup.last_bytes_xferred or 0,
                          is_upload = soup.is_upload or 0)

            for key in kwargs:
                try:
                    kwargs[key] = kwargs[key].text # ok if soup stuff
                except AttributeError:
                    pass

            return Task_fileTransfer(**kwargs)
        except Exception as e:
            logger.exception('Trying to create task out of {}, got'.format(xml))

class Task_web(Task):
    fmt_date = '%d %b %Y %H:%M:%S UTC'

    def __init__(self, claimedCredit='0', grantedCredit='0', **kwargs):
        self.setGrantedCredit(grantedCredit) # stored as float
        self.setClaimedCredit(claimedCredit) # stored as float
        super(Task_web, self).__init__(**kwargs)

    @staticmethod
    def createFromHTML(data):
        logger.debug('creating from %s', data)
        assert len(data) == 9, 'vops, data not recognized %s, len = %s' % (data, len(data))
        name = data[0]
        workUnitId = data[1]    # not used
        device = data[2]
        sentTime = data[3]      # not used
        deadline = data[4]
        state = data[5]
        clockTime = data[6]     # not used
        CPUtime = data[7]
        grantedCredit = data[8]
        return Task_web(name=name, device=device,
                        deadline=deadline, state=state,
                        elapsedCPUtime=CPUtime, grantedCredit=grantedCredit)

    def toString(self):
        s = super(Task_web, self).toString()
        s.extend([self.claimedCredit_str, self.grantedCredit_str])
        return s

    @property
    def grantedCredit_str(self):
        return str(self.grantedCredit)

    def setGrantedCredit(self, grantedCredit):
        if grantedCredit == 'pending':
            grantedCredit = '0'
        self.grantedCredit = self.toFloat(grantedCredit)

    @property
    def claimedCredit_str(self):
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
        elif state.lower().startswith('aborted'):
            state = 'aborted'
        if 'error' in state.lower():
            state = 'error'

        super(Task_web, self).setState(state)

class Task_web_worldcommunitygrid(Task_web):
    fmt_date = '%m/%d/%y %H:%M:%S'
    def strToTimedelta(self, hours):
        return datetime.timedelta(hours=self.toFloat(hours))

    @staticmethod
    def createFromHTML(data):
        assert len(data) == 7, 'vops, data not recognized %s' % data

        name = data[0]
        device = data[1]
        state = data[2]
        sentTime = data[3]      # not used
        deadline = data[4]
        
        time = data[5].encode('ascii', errors='ignore').split('/')
        CPUtime = time[0]
        clockTime = time[1]     # not used
        
        credit = data[6].encode('ascii', errors='ignore').split('/')
        claimedCredit = credit[0]
        grantedCredit = credit[1]
        return Task_web_worldcommunitygrid(name=name, device=device,
                                           state=state, 
                                           elapsedCPUtime=CPUtime, deadline=deadline,
                                           claimedCredit=claimedCredit, grantedCredit=grantedCredit)

class Task_web_yoyo(Task_web):
    @staticmethod
    def createFromHTML(data):
        assert len(data) == 9, 'vops, data not recognized %s' % data

        name = data[0]
        sentTime = data[1]      # Not used
        deadline = data[2]
        state = " ".join(data[3:6])
        CPUtime = data[6]
        
        claimedCredit = data[7]
        grantedCredit = data[8]
        return Task_web_yoyo(name=name, device='',
                             state=state, 
                             elapsedCPUtime=CPUtime, deadline=deadline,
                             claimedCredit=claimedCredit, grantedCredit=grantedCredit)

class Task_web_climateprediction(Task_web):
    @staticmethod
    def createFromHTML(data):
        logger.debug('creating from %s', data)
        assert len(data) == 10, 'vops, data not recognized %s, len = %s' % (data, len(data))
        name = data[0]
        workUnitId = data[1]    # not used
        device = data[2]
        sentTime = data[3]      # not used
        deadline = data[4]
        state = data[5]
        clockTime = data[6]     # not used
        CPUtime = data[7]
        claimedCredit = data[8]
        grantedCredit = data[9]
        return Task_web(name=name, device=device,
                        deadline=deadline, state=state,
                        elapsedCPUtime=CPUtime, 
                        claimedCredit=claimedCredit, grantedCredit=grantedCredit)

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
        super(Task_jobLog, self).__init__(name=name, fractionDone='100',
                                          elapsedCPUtime=ct, remainingCPUtime='0')
        self.setTime(time)
        # Lets just keep it simple, float already has a sane str() version
        self.estimated_runtime_uncorrected = float(ue)
        self.final_cpu_time = float(ct)
        self.rsc_fpops_est = float(fe)
        self.final_elapsed_time = float(et)

    @staticmethod
    def createFromJobLog(line):
        """
        Expects a single line from the job log file
        """
        s = line.split()
        assert len(s) in (11, 13), 'Line in job log not recognized {0} "{1}" -> "{2}"'.format(len(s), line, s)
        return Task_jobLog(time=s[0], name=s[8],
                           ue=s[2], ct=s[4], fe=s[6], et=s[10])

    def setTime(self, value):
        t = int(value)
        self.time = datetime.datetime.fromtimestamp(t)

def adjustColumnSpacing(tasks):
    """
    Not Thread safe, modifies the Task.columnSpacing for equal columns.
    Call this before printing list of tasks
    """
    for t in tasks:
        for ix, item in enumerate(t.toString()):
            Task.columnSpacing['col%d' % ix] = max(Task.columnSpacing['col%d' % ix], len(item))
