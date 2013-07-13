#!/usr/bin/env python
# Standard python
from socket import socket
import logging
logger = logging.getLogger('boinc.boinccmd')
# This project
from project import Project, pretty_print

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
        #print 'BUF', buf
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

def get_state(command='get_state', printRaw=False):
    projects = list()
    with Boinccmd() as s:
        currentBlock = []
        inBlock = False
        appNames = dict()       
        for line in s.request(command):
            if printRaw:
                print line

            if line.strip() in ('<project>', '<app>', '<workunit>', '<result>'):
                inBlock = True

            reset = True
            if '</project>' in line:
                project = Project.createFromXML("\n".join(currentBlock))
                projects.append(project)
                logger.debug('project %s', project)
            elif '</app>' in line:
                application = project.appendApplicationFromXML("\n".join(currentBlock))
                logger.debug('application %s', application)
            elif '</workunit>' in line:
                workunit = project.appendWorkunitFromXML("\n".join(currentBlock))
                logger.debug('workunit, %s', workunit)
            elif '</result>' in line:
                try:
                    t = project.appendResultFromXML("\n".join(currentBlock))
                    logger.debug('result, %s', t)
                except KeyError:
                    logging.exception('Could not append task to application:')
            else:
                reset = False

            if reset:
                inBlock = False
                currentBlock = []                

            if inBlock:
                currentBlock.append(line.strip())

    return projects

if __name__ == '__main__':
    import argparse

    from loggerSetup import loggerSetup

    parser = argparse.ArgumentParser(description='Runs and parses get_state rpc reply')
    parser.add_argument('command', default='get_state', choices=['get_state', 'get_project_status'], nargs='?')
    parser.add_argument('-r', '--raw', action='store_true', help='Print out the raw xml')
    parser.add_argument('--show_empty', action='store_true', help='Show empty projects (no tasks)')
    args = parser.parse_args()

    loggerSetup(logging.INFO)
    projects = get_state(command=args.command,
                         printRaw=args.raw)

    pretty_print(projects, 
                 show_empty=args.show_empty)
