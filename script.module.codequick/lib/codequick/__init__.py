# -*- coding: utf-8 -*-
# Copyright: (c) 2016 - 2017 William Forde (willforde+codequick@gmail.com)
# License: GPLv2, see LICENSE for more details
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Execution start time, used later to report total execution time
from __future__ import absolute_import
start_time = __import__("time").time()

# Package imports
from codequick.storage import PersistentDict, PersistentList
from codequick.support import dispatcher as _dispatcher
from codequick.api import Script, Route, Resolver
from codequick.listing import Listitem
from codequick import utils

# Convenience function to call dispatcher
run = _dispatcher.dispatch
