# Standard python
import re
# Non standard
# Project imports
from plot.jobLog import JobLog

class Project(object):
    def __init__(self, url, userid, password, username):
        self.name = url
        self.user = dict(userid=userid, password=password, username=username)
        self.applications = dict()
        self.update()
        
    def update(self):
        self.statistics_jobLog = self.get_jobLog()
        self.statistics_ = None

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
        self.name_short = name.replace('https://', '')
        self.name_short = self.name_short.replace('http://', '')
        self.name_short = self.name_short.replace('www.', '')
        self.name_short = self.name_short.replace('.org', '')

    def get_jobLog(self):
        filename = None
        with open(filename, 'r') as f:
            data = self.parse_jobLog(f)
        return data
    
    def parse_jobLog(self, f):
        """
        ue - estimated_runtime_uncorrected
        ct - final_cpu_time, cpu time to finish
        fe - rsc_fpops_est, estimated flops
        et - final_elapsed_time, clock time to finish
        """
        data = JobLog()
        now = datetime.datetime.now()
        for line in f:
            s = line.split()
            assert len(s) == 11, 'Line in job log not recognized {0} "{1}" -> "{2}"'.format(len(s), line, s)
            t = int(s[0])
            t = datetime.datetime.fromtimestamp(t)
            if limitDaysToPlot == None or now - t < limitDaysToPlot:
                data.time.append(t)
                data.ue.append(float(s[2]))
                data.ct.append(float(s[4]))
                data.fe.append(float(s[6]))
                data.names.append(s[8])
                data.et.append(float(s[10]))
        return data
