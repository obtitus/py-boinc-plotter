"""
Parses boinccmd xml outputs
"""
# non standard:
from bs4 import BeautifulSoup
# this project:
from project import Project
from statistics import Statistics
from application import Application
from task import Task_local

def project(xml):
    soup = BeautifulSoup(xml, "xml")
    #print soup.prettify()
    pref = 'Resource share {:.3g}%'.format(float(soup.resource_share.text))
    if soup.dont_request_more_work is not None:
        pref += ", Don't request more work"
    s = Statistics(soup.user_total_credit.text,
                   soup.user_expavg_credit.text,
                   soup.host_total_credit.text,
                   soup.host_expavg_credit.text)
    return Project(soup.master_url.text, statistics=s, settings=pref)
    
def application(xml):
    soup = BeautifulSoup(xml, "xml")
    short = soup.find('name').text # Vops: soup.name is 'reserved' so need to use find('name')
    long  = soup.find('user_friendly_name').text
    name = "{} ({})".format(long, short)
    return Application(name)

def task(xml):
    soup = BeautifulSoup(xml, "xml")
    return Task_local(name=soup.wu_name.text,
                      state=soup.state.text,
                      fractionDone=soup.fraction_done.text,
                      elapsedCPUtime=soup.elapsed_time.text,
                      remainingCPUtime=soup.estimated_cpu_time_remaining.text,
                      deadline=soup.report_deadline.text,
                      schedularState=soup.scheduler_state.text,
                      active=soup.active_task_state.text)
