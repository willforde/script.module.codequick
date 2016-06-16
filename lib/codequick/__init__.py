""""
Copyright: (c) 2013 - 2016 William Forde (willforde+codequick@gmail.com)
License: GPLv3, see LICENSE for more details

codequick is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

codequick is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

# Standard Library Imports
import sys

# Import the fastest json serializer
if sys.version_info >= (2, 7):
    import json
else:
    try:
        import simplejson as json
    except:
        import json

# Package imports
from .api import localized, route, run
from .inheritance import VirtualFS, Executer, PlayMedia, PlaySource
from .youtube import YoutubeBase

__all__ = ["VirtualFS", "PlayMedia", "PlaySource", "YoutubeBase", "localized", "route", "run", "json"]
