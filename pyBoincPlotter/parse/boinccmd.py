"""
Parses boinccmd xml outputs
"""
# non standard:
from bs4 import BeautifulSoup
# this project:
from project import Project
from statistics import Statistics

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
    
