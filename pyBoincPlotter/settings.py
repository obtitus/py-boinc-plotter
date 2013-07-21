
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
import collections
import logging
logger = logging.getLogger('boinc.settings')

class Settings(collections.namedtuple('Settings', ['resource_share', 'dont_request_more_work', 'sched_priority'])):
    """
    Some of the project settings
    """
    @staticmethod
    def createFromSoup(soup):
        res = dict(resource_share = soup.resource_share,
                   sched_priority = soup.sched_priority)
        for key in res:
            if res[key] != None:
                res[key] = float(res[key].text)
                
        dont_request_more_work = soup.dont_request_more_work != None

        return Settings(dont_request_more_work=dont_request_more_work, **res)

    def __str__(self):
        ret = ''
        if self.resource_share is not None:
            ret += 'Resource share {:.3g}%'.format(self.resource_share)
        if self.sched_priority is not None:
            ret += ', sched. priority {:.3g}'.format(self.sched_priority)
        if self.dont_request_more_work:
            ret += ", Don't request more work"
            
        return ret
