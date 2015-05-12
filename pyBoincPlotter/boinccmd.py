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
"""Speaks to boinc both thorugh rpc calls and the command line boinccmd"""
# Standard python
import os
import subprocess
import shlex
from socket import socket
import logging
logger = logging.getLogger('boinc.boinccmd')
# This project
from project import Project, Project_fileTransfers, pretty_print
from task import Task_fileTransfer

class CallBoinccmd(object):
    """ tiny layer on top of subprocess Popen for calling boinccmd and getting stdout """
    def __init__(self, boinc_dir, arguments='--get_state'):
        if isinstance(arguments, basestring):
            arguments = shlex.split(arguments)

        boinccmd = os.path.join(boinc_dir, 'boinccmd')
        if not(os.path.exists(boinccmd)):
            boinccmd = 'boinccmd' # lets hope its on the $PATH
        cmd = [boinccmd]
        cmd.extend(arguments)
        logger.info('cmd: %s', cmd)
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                            cwd=boinc_dir)
        except Exception as e:
            logger.error('Error when running %s, e = "%s"', cmd, e)
            self.process = None

    def communicate(self, returnAll=False):
        if self.process != None:
            stdout, stderr = self.process.communicate()
            if returnAll:               # hack.
                return stdout + stderr
            
            if stderr != '':
                print "Error: {}".format(stderr)
                return ''
            return stdout

class Boinccmd(socket):
    def __init__(self, addr='', portNr=31416, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.previous_data = ''
        self.addr = addr
        self.portNr = portNr
    
    def __enter__(self):
        self.connect((self.addr, self.portNr))
        return self
    def __exit__(self, type, value, traceback):
        self.close()

    def request(self, command):
        buf = "<boinc_gui_rpc_request>\n"\
               "<%s/>\n"\
               "</boinc_gui_rpc_request>\n\003"\
               % (command)
        self.sendall(buf)
        return self.recv_end()

    def recv_end(self):
        """ Iterator over lines of self.recv()
        """
        End = '\003'
        more_data = True
        while more_data:
            data = self.previous_data + self.recv(4096) # previous data gets included
            data = data.split('\n')
            self.previous_data = ''

            for line_ix in xrange(len(data)): # For each line
                if End in data[line_ix]:
                    more_data = False # breaks outer loop
                    break             # breaks inner loop
                elif line_ix == len(data)-1: # no endmark and last line
                    self.previous_data = data[line_ix]
                else:
                    yield data[line_ix]

            ix = data[line_ix].find(End) # yield until End mark
            if ix != -1:
                yield data[line_ix][:ix]
                self.previous_data += data[line_ix][:ix]

def get_state_command(command='get_state', printRaw=False, projects=None):
    parser = Parse_state(projects)
    with Boinccmd() as s:
        for line in s.request(command):
            if printRaw:
                print line

            parser.feed(line)

    return parser.projects

def get_state(printRaw=False):
    d1 = get_state_command('get_state', printRaw=printRaw)
    d2 = get_state_command('get_file_transfers', printRaw=printRaw, projects=d1)
    return d2

class Parse_state(object):
    def __init__(self, projects=None):
        self.currentBlock = []
        self.inBlock = False
        if projects is not None:
            self.projects = projects
        else:
            self.projects = dict()

        # Current state:
        self.c_proj = None
        self.c_app  = None
        self.c_task = None

    def feed(self, line):
        if line.strip() in ('<project>', '<app>', '<workunit>', '<result>', '<file_transfer>'):
            self.inBlock = True

        reset = True
        if '</project>' in line:
            self.c_proj = Project.createFromXML("\n".join(self.currentBlock))
            self.projects[self.c_proj.url] = self.c_proj
            logger.debug('project %s', self.c_proj)
        elif '</app>' in line:
            self.c_app = self.c_proj.appendApplicationFromXML("\n".join(self.currentBlock))
            logger.debug('application %s', self.c_app)
        elif '</workunit>' in line:
            self.c_task = self.c_proj.appendWorkunitFromXML("\n".join(self.currentBlock))
            logger.debug('task, %s', self.c_task)
        elif '</result>' in line:
            try:
                t = self.c_proj.appendResultFromXML("\n".join(self.currentBlock))
                logger.debug('result, %s', t)
            except KeyError:
                logging.exception('Could not append task to application:')
        elif '</file_transfer>' in line:
            t = Task_fileTransfer.createFromXML("\n".join(self.currentBlock))
            p = Project(url=t.project_url, name=t.project_name)
            
            if not(self.projects.has_key(t.project_url)):
                logger.debug('Hmm, projects does not have key "%s", %s', t.project_url, self.projects)
                self.projects[t.project_url] = p
            logger.debug('appending file_transfer %s', t)
            self.projects[p.url].fileTransfers.append(t)
        else:
            reset = False

        if reset:
            self.inBlock = False
            self.currentBlock = []                

        if self.inBlock:
            self.currentBlock.append(line.strip())

if __name__ == '__main__':
    import argparse

    from loggerSetup import loggerSetup

    parser = argparse.ArgumentParser(description='Runs and parses get_state rpc reply')
    parser.add_argument('command', default='get_state', nargs='?', choices=['get_state', 
                                                                            'get_file_transfers', 
                                                                            'get_project_status',
                                                                            'get_cc_status'])
    parser.add_argument('-r', '--raw', action='store_true', help='Print out the raw xml')
    parser.add_argument('--show_empty', action='store_true', help='Show empty projects (no tasks)')
    args = parser.parse_args()

    loggerSetup(logging.DEBUG)
    if args.command == 'get_cc_status':
        import config
        _, _, BOINC_DIR = config.set_globals()
        c = CallBoinccmd(BOINC_DIR, '--get_cc_status')
        print c.communicate(returnAll=True)
    else:
        projects = get_state_command(command=args.command,
                                     printRaw=args.raw)
        pretty_print(projects, 
                     show_empty=args.show_empty)
