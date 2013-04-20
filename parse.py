"""
Parsing
"""
import re
from HTMLParser import HTMLParser

import task
import project

#import xml

import logging
logger = logging.getLogger('boinc.parse')

# Only contains info on currently running tasks, but contains slot number and short name
# class InitDataParser(task.Task):
#     # Parse a init_data.xml file into a single task.Task object
#     def __init__(self, page):
#         Task.__init__(self)
#         self.parse()
        
#     def parse(self)
#         tree = xml.etree.ElementTree.parse(page)
#         self.name = tree.find('result_name')

def shortLongName(projectName):
    name_re = re.match('([^(]+)\((\w+)\)', projectName)
    name_short = ''
    name_long = projectName.replace(name_short, '') # hack                
    if name_re:
        name_long = name_re.group(1)                    
        name_short = name_re.group(2)

    logger.debug('short long name called with %s -> (%s, %s)', projectName, name_long, name_short)
    return name_long.strip(), name_short.strip()
                    
class CMDparser(object):
    # Parses output from boinccmd --get_state
    class State(dict):
        # Internal state, which part of the output are we parsing?
        def __init__(self, parser):
            dict.__init__(self, {'Projects': [False, parser.parseProject],
                                 'Applications': [False, parser.parseApplications],
                                 'Application versions': [False, parser.parseApplicationsVersions],
                                 'Workunits': [False, parser.parseWorkunits],
                                 'Tasks': [False, parser.parseTasks],
                                 'Time stats': [False, parser.parseTimeStats]})
        def switchState(self, key):
            # Switch state 'key' to true and set all others false
            for k in self:
                self[k][0] = False
            self[key][0] = True

        def callParser(self, line):
            # call parsers where state is true
            for k in self:
                if self[k][0]:self[k][1](line)

    def __init__(self):
        self.state = self.State(self)
        self.info = ''
        self.tasks = list()
        self.projects = list()

    def parseLine(self, line):
        heading = re.match("======== ([\w ]*) ========", line)
        if heading != None:
            key = heading.group(1)
            assert key in self.state, 'Could not find "{}" in known states'.format(key)
            self.state.switchState(key)
        else:
            self.state.callParser(line)

    def splitColon(self, line):
        if ':' in line:
            split = line.split(':')
            name = split[0].strip()
            value = ":".join(split[1:]).strip()
            return name, value
        else:
            return None, None
        
    def parseProject(self, line):
        name, value = self.splitColon(line)
        if name == 'master URL': self.info += '{}\n'.format(value)        
        if name == 'user_name': self.info += 'User: {}\n'.format(value)
        if name == 'user_total_credit': self.info += 'Total boinc credits: {:.0f}\n'.format(float(value))
        if name == 'user_expavg_credit': self.info += 'Average boinc credits: {:.0f}\n'.format(float(value))

    def parseApplications(self, line):
        name, value = self.splitColon(line)
        if name == 'name':
            self.projects.append(project.Project(name_short = value))
            
    def parseApplicationsVersions(self, line):
        pass
    def parseWorkunits(self, line):
        pass
    def parseTasks(self, line):
        #print 'line', line
        if re.match('[\d]*\) -----------', line):
            self.task = task.Task() # new task
            self.tasks.append(self.task)
            
        name, value = self.splitColon(line)
        if name == 'name':
            self.task.name = value
        elif name == 'ready to report':
            self.task.readyToReport = value
        elif name == 'fraction done':
            self.task.fractionDone = value
        elif name == 'final CPU time':
            self.task.finalCPUtime = value
        elif name == 'current CPU time':
            self.task.currentCPUtime = value
        elif name == 'estimated CPU time remaining':
            self.task.remainingCPUtime = value
        elif name == 'report deadline':
            self.task.deadline = value
        elif name == 'state':
            self.task.state = value
        elif name == 'active_task_state':
            self.task.active = value
        elif name == 'scheduler state':
            self.task.schedularState = value
        else:
            pass
            #print('ignoring', name, value)
            
    def parseTimeStats(self, line):
        pass

    def __str__(self):
        ret = self.info
        try:
            h = self.tasks[0].header
            ret += h + '\n'
            ret += len(h)*'-' + '\n'
        except IndexError: pass
        for task in self.tasks:
            ret += str(task) + '\n'
        return ret

    def feed(self, page):
        for line in page.split('\n'):
            self.parseLine(line)
    

class HTMLParser_worldcommunitygrid(HTMLParser):
    def __init__(self, browser):
        self.inTitle = False
        self.inDiv = False # div section at top, contains short and long project names
        self.inTable = False
        self.inData = False
        self.inFullName = False

        self.current_shortName = ''             # Set in starttage from the url
        self.projects = dict() # key is long name, value is a project.Project() object

        self.current_data = ''          # Append everything in td tags (which is also in a table)
        
        self.currentTask = list()
        self.tasks = list()
        self.listOfPages = list() # unique reference to other pages (1, 2, 3)...

        self.browser = browser
        self.parse_workUnit = HTMLParser_worldcommunitygrid_workunit()
        HTMLParser.__init__(self)
        
    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.inTitle = True
        elif tag == 'table':
            self.inTable = True
        elif tag == 'div':
            self.inDiv = True

        if self.inTable and tag == 'td':
            self.inData = True

        if self.inTable and tag == 'a':
            # Try to find reference to other pages
            if attrs[0][0] == 'href':
                url = attrs[0][1]
                reg = re.search('pageNum=(\d*)', url) # Look for multiple pages
                if reg and reg.group(1) != '':
                    res = reg.group(1)
                    if res not in self.listOfPages: self.listOfPages.append(res)

                reg = re.search("javascript:addHostPopup\('/ms/device/viewWorkunitStatus.do\?workunitId=(\d*)'", url) # Look for detailed work information
                if reg:
                    workId = reg.group(1)
                    url = 'http://www.worldcommunitygrid.org/ms/device/viewWorkunitStatus.do?workunitId={}'.format(workId)
                    content = self.browser.visitURL(url)
                    self.parse_workUnit.feed(content)
                    self.currentTask.append(self.parse_workUnit.projectName)
            
        if self.inDiv and tag == 'a':
            # Try to find short and long project names
            if attrs[0][0] == 'href':
                url = attrs[0][1]
                reg = re.search('research/(\w*)/overview.do', url)
                if reg:
                    self.current_shortName = reg.group(1)
                    self.inFullName = True
                    
            
    def handle_endtag(self, tag):
        if tag == 'title':
            self.inTitle = False
        elif tag == 'div':
            self.inDiv = False
        elif tag == 'td':
            self.inData = False
            if self.current_data != '':
                self.currentTask.append(self.current_data)
                self.current_data = ''
        elif tag == 'tr':
            if len(self.currentTask) == 8:
                self.tasks.append(task.WebTask_worldcommunitygrid(self.currentTask))
            elif len(self.currentTask) != 0:
                pass
                #print len(self.currentTask), self.currentTask
            self.currentTask = list() # new

    def handle_data(self, data):
        if self.inTitle:
            self.title = data
        if self.inData:
            data = data.strip()
            self.current_data += data
        if self.inFullName:
            name_long, name_short = shortLongName(data)
            if name_short == '':
                name_short = self.current_shortName
            self.projects[name_long] = project.Project(name_long, name_short)
            self.inFullName = False

    def __str__(self):
        s = ''
        for project in self.projects:
            s += self.projects[project].__str__() + '\n'
        for task in self.tasks:
            s += task.__str__() + '\n'
        return s

    def feed(self, *args, **kwargs):
        HTMLParser.feed(self, *args, **kwargs)

        # Lets check if there are additional pages we should visit (browser keeps track so that we don't bombard the same page multiple times)
        for page in self.listOfPages:
            content = self.browser.visit(page)
            if content != '':
                self.feed(content) # recursion!
        

class HTMLParser_worldcommunitygrid_workunit(HTMLParser):
    # Parses the workunit info page, example: http://www.worldcommunitygrid.org/ms/device/viewWorkunitStatus.do?workunitId=660908836
    def __init__(self):
        self.inSpan = False
        self.inProjectName = False
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'span':
            if attrs[0] == ('class', 'contentText'):
                self.inSpan = True
        
    def handle_endtag(self, tag):
        if tag == 'span': self.inSpan = False

    def handle_data(self, data):
        if self.inSpan:
            if data.strip() == 'Project Name:':
                self.inProjectName = True
            elif self.inProjectName: # Next time
                self.projectName = data
                self.inProjectName = False # reset
    
class HTMLParser_boinc(HTMLParser):
    def __init__(self, tasks=None, projects=None):
        # State:
        self.inTable = False
        self.inTr = False
        self.currentTask = list()
        HTMLParser.__init__(self)
        # Public:
        if tasks == None:
            self.tasks = list()
        else:
            self.tasks = tasks
        if projects == None:
            self.projects = dict()
        else:
            self.projects = projects

    def handle_starttag(self, tag, attrs):
        if tag == 'table' and len(attrs) == 2: # Only the main table seems to have 2 entries (for now!)
            self.inTable = True
        if tag == 'tr' and self.inTable:
            self.inTr = True
        
    def handle_endtag(self, tag):
        if tag == 'table':
            self.inTable = False
        if tag == 'tr':
            self.inTr = False
            logger.debug('%s %s', self.currentTask, len(self.currentTask))
            if len(self.currentTask) == 10:
                name_long, name_short = shortLongName(self.currentTask[9])
                self.currentTask[9] = name_long
                t = task.WebTask(self.currentTask)
                self.tasks.append(t)
                self.projects[name_long] = project.Project(name_long=name_long,
                                                           name_short=name_short) # hack
            self.currentTask = list()

    def handle_data(self, data):
        if self.inTable and self.inTr:
            if data.strip() != '':
                self.currentTask.append(data)

if __name__ == '__main__':
    import browser
    logger = logging.getLogger('boinc')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    import config
    config.main()
    browser.main()
    
    browser = browser.Browser('mindmodeling.org')

    parser = HTMLParser_boinc()
    content = browser.visit()
    #print content
    parser.feed(content)
    #print parser
