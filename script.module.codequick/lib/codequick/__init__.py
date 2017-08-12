# -*- coding: utf-8 -*-
# Copyright: (c) 2016 - 2017 William Forde (willforde+codequick@gmail.com)
# License: GPLv3, see LICENSE for more details
#
# codequick is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# codequick is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Execution start time, used later to report total execution time
from __future__ import absolute_import
start_time = __import__("time").time()

# Package imports
from codequick.api import Script, Route, Resolver, run
from codequick.storage import PersistentDict, PersistentList
from codequick.listing import Listitem
from codequick import utils

# Notification icon options
NOTIFICATION_WARNING = 'warning'
NOTIFICATION_ERROR = 'error'
NOTIFICATION_INFO = 'info'
