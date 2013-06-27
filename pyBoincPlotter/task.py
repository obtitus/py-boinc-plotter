#!/usr/bin/env python
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
Classes to represent a single workunit/task,
Task is for local task while WebTask is for tasks from worldcommunitygrids results status page
"""
import os
import subprocess
import datetime

import logging
logger = logging.getLogger('boinc.task')

from loggerSetup import loggerSetup
import config

class Task(object):
    # Each property as a variable for the python object _<property>
    # and a set <property> for converting from a string
    # and a get <property> for returning a string representation

    desc_state = ['downloading', 'ready to run', 'running', 'suspended', 'paused', 'computation completed', 'uploading', 'ready to report']
    desc_active = ['paused', 'running', 2, 3, 4, 5, 6, 7, 8, 'running']
    desc_schedularState = ['ready to start', 'suspended', 'running']

    def strToTimedelta(self, sec):
        timedelta = datetime.timedelta(seconds=float(sec))
        return timedelta

    def timedeltaToStr(self, timedelta):
        timedelta = str(timedelta)
        ix = timedelta.find('.')
        if ix != -1:
            timedelta = timedelta[:ix]
        return timedelta

    def __init__(self):

        self.fmt_date = '%a %b %d %H:%M:%S %Y'
        #self.fmt = "{self.name:<20} {stateDesc:<15} {self.fractionDone:<5} {self.currentCPUtime:<10} {self.remainingCPUtime:<10} {self.deadline:<25} {self.state} {self.active} {self.schedularState}"
        self.fmt = "{self.nameShort:<20} {self.state:<20} {self.fractionDone:<5} {self.currentCPUtime:<10} {self.remainingCPUtime:<10} {self.deadline:<25} {self.claimed:>5} {self.granted:>5} {self.device:>20}"
        self.header = self.fmt.replace('self.', '')
        self.header = self.header.format(nameShort="Name", state="State", fractionDone="Done",
                                         currentCPUtime='Current', remainingCPUtime="Remaining",
                                         deadline="Deadline/Return time",
                                         claimed="Claimed", granted='Granted', device='Device')
        # These are given meaning in subclass webTask
        self.claimed = 0
        self.granted = 0
        self.device = 'localhost'
    
    def __str__(self):            
        return self.fmt.format(self=self)

    def done(self):
        # Is the task finished?
        if self.desc_state[self._state] == 'in progress': # For tasks on other computers
            return False
        else:
            return self.remainingCPUtime == '0:00:00'
    def isWebTask(self):
        return isinstance(self, WebTask_worldcommunitygrid) or \
               isinstance(self, WebTask)
            
    @property
    def name(self):
        return self._name
    @property
    def nameShort(self):
        if len(self._name) > 15:
            return self._name[:15] + '...'
        else:
            return self._name        
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def deadline(self):
        # Return time until deadline
        now = datetime.datetime.today()
        delta = self._deadline - now
        s = self.timedeltaToStr(delta)
        if delta.days < 0:
            delta = now - self._deadline
            s = '-' + self.timedeltaToStr(delta)
        return s
    @deadline.setter
    def deadline(self, deadline):
        self._deadline = datetime.datetime.strptime(deadline, self.fmt_date)

    @property
    def readyToReport(self):
        return self._readyToReport
    @readyToReport.setter
    def readyToReport(self, readyToReport):
        self._readyToReport = readyToReport
    
    @property
    def finalCPUtime(self):
        return self.timedeltaToStr(self._finalCPUtime)
    @finalCPUtime.setter
    def finalCPUtime(self, finalCPUtime):
        self._finalCPUtime = self.strToTimedelta(finalCPUtime)

    @property
    def state(self):
        state = self.desc_state[self._state]
        # Hack
        if self.remainingCPUtime == '0:00:00' and not(state == 'in progress') and self._schedularState != -1: # done and not on other computer
            self.fractionDone = '1' # this is set to 0 when done, weird!
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
    
    @state.setter
    def state(self, state):
        try:
            self._state = int(state)
        except ValueError:  # lets hope its a string representing the state
            try:
                self._state = self.desc_state.index(state.lower())
            except:                     # guess not
                self.desc_state.append(state.lower())  # now it is!
                self._state = self.desc_state.index(state.lower())
    
    @property
    def active(self):
        return self.desc_active[self._active]
    @active.setter
    def active(self, active):
        self._active = int(active)

    @property
    def schedularState(self):
        return self.desc_schedularState[self._schedularState]

    @schedularState.setter
    def schedularState(self, schedularState):
        self._schedularState = int(schedularState)
    
    @property
    def currentCPUtime(self):
        if self.done():
            self._currentCPUtime = self._finalCPUtime
        return self.timedeltaToStr(self._currentCPUtime)

    @currentCPUtime.setter
    def currentCPUtime(self, currentCPUtime):
        self._currentCPUtime = self.strToTimedelta(currentCPUtime)
    
    @property
    def fractionDone(self):
        if self.done():
            self._fractionDone = 100
        return "{:.0f} %".format(self._fractionDone)

    @fractionDone.setter
    def fractionDone(self, fractionDone):
        self._fractionDone = float(fractionDone)*100
    
    @property
    def remainingCPUtime(self):
        return self.timedeltaToStr(self._remainingCPUtime)

    @remainingCPUtime.setter
    def remainingCPUtime(self, remainingCPUtime):
        self._remainingCPUtime = self.strToTimedelta(remainingCPUtime)

    @property
    def granted(self):
        return self._granted

    @granted.setter
    def granted(self, granted):
        if hasattr(granted, 'replace'):
            granted = granted.replace(',', '')
            granted = granted.replace('---', '0')

        try:
            self._granted = float(granted)
        except ValueError:
            self._claimed = granted

    @property
    def claimed(self):
        return self._claimed

    @claimed.setter
    def claimed(self, claimed):
        if hasattr(claimed, 'replace'):
            claimed = claimed.replace(',', '')
            claimed = claimed.replace('---', '0')

        try:
            self._claimed = float(claimed)
        except ValueError:
            self._claimed = claimed

class WebTask_worldcommunitygrid(Task):
    desc_state = ['in progress', 'aborted', 'detached', 'error', 'no reply', 'pending validation', 'pending verification', 'valid', 'invalid', 'inconclusive', 'too late', 'waiting to send', 'other']
    def strToTimedelta(self, hours):
        timedelta = datetime.timedelta(hours=float(hours))
        return timedelta

    def __init__(self, lst):
        Task.__init__(self)
        
        self.fmt_date = '%m/%d/%y %H:%M:%S'
        # example lst: ['Human Proteome Folding - Phase 2', 'qn391_ 00116_ 3--', '1x-193-157-192-27.uio.no', 'Valid', '2/25/13 16:05:58', '2/26/13 15:03:24', '5.43 / 5.62', '89.2/127.7']
        
        assert len(lst) == 8, 'Error, could not recognized task {0}'.format(lst)
        self.projectName = lst[0]
        self.name = lst[1].replace('--', '').replace(' ', '')
        
        self.device = lst[2]
        self.state = lst[3]

        self.sent = lst[4]
        self.deadline = lst[5]

        split = lst[6].split('/')
        self.finalCPUtime = split[0]
        self.timeHours = split[1]

        split = lst[7].split('/')
        self.claimed = split[0]
        self.granted = split[1]

        self._currentCPUtime = self._finalCPUtime
        self.remainingCPUtime = 0

        # We need to override these
        self.schedularState = -1
        self.active = 0
        self.fractionDone = 0

class WebTask(Task):
    desc_state = ['in progress', 'validation pending', 'validation inconclusive', 'valid', 'invalid', 'error']
    def __init__(self, name, workunit, device, sent, deadline, state, finaltime, finalCPUtime, granted, projectName, claimed=0):
        Task.__init__(self)
        
        self.fmt_date = r'%d %b %Y %H:%M:%S UTC'
        # example lst: ['MindModeling-433-51616f73ef41a_0', '5649272', '35054', '7 Apr 2013, 13:13:03 UTC', '8 Apr 2013, 20:13:03 UTC', 'In progress', '---', '---', '---', 'Native Python v2.7 Application v1.02 (sse2)']
        #assert len(lst) == 10, 'Error, could not recognized task {0}'.format(lst)

        self.name = name

        self.workunit = workunit

        self.device = device

        self.sent = sent              # TODO: add this to print?

        self.deadline = deadline.replace(',', '').replace('|', '') # some write: '%d %b %Y[,|] %H:%M:%S UTC'

        # Hack!
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
        self.state = state

        self.finaltime = finaltime

        if finalCPUtime == '---':
            finalCPUtime = '0'
        else:
            finalCPUtime = finalCPUtime.replace(',', '') # used as thousand seperator
        self.finalCPUtime = finalCPUtime

        self.granted = granted
        self.claimed = claimed

        self.projectName = projectName

        # We need to override these
        self.remainingCPUtime = 0
        self._currentCPUtime = self._finalCPUtime        
        self.schedularState = -1
        self.active = 0
        self.fractionDone = 0

class BoincCMD(object):
    # tiny layer on top of subprocess Popen for calling boinccmd and getting stdout
    def __init__(self, argument='--get_state', boinc_dir=None):
        if boinc_dir == None:
            self.boinc_dir = config.BOINC_DIR
        else:
            self.boinc_dir = boinc_dir

        cmd = [os.path.join(self.boinc_dir, 'boinccmd')]
        #cmd.append(argument)
        cmd.extend(argument.split(' '))        
        logger.info('cmd: %s', cmd)
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.boinc_dir)
        except Exception as e:
            logger.error('Error when running %s, e = "%s"', cmd, e)
            self.process = None

    def communicate(self):
        if self.process != None:
            stdout, stderr = self.process.communicate()
            if stderr != '':
                print "Error: {}".format(stderr)
                return ''
            return stdout

if __name__ == '__main__':
    loggerSetup(logging.INFO)
    p1 = Boinccmd('--get_cc_status')
    p2 = boinccmd('--get_state')    
    print p1.communicate()
    print p2.communicate()
