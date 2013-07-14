import collections
import logging
logger = logging.getLogger('boinc.settings')

class Settings(collections.namedtuple('Settings', ['resource_share', 'dont_request_more_work', 'sched_priority'])):
    """
    Some of the project settings
    """
    @staticmethod
    def createFromSoup(soup):
        resource_share = float(soup.resource_share.text)
        dont_request_more_work = soup.dont_request_more_work != None
        sched_priority = float(soup.sched_priority.text)
        return Settings(resource_share=resource_share,
                        dont_request_more_work=dont_request_more_work,
                        sched_priority=sched_priority)

    def __str__(self):
        ret = 'Resource share {:.3g}%, sched. priority {}'.format(self.resource_share,
                                                                  self.sched_priority)
        if self.dont_request_more_work:
            ret += ", Don't request more work"
        return ret
