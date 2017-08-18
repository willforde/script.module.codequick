# Standard Library Imports
import urlparse
import logging
import sys
import os

# Package imports
from codequickcli.support import AddonDB

# Initialize Database of addons
addon_db = AddonDB()

# Base logger
logger = logging.getLogger("codequickcli")
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter("%(relativeCreated)-13s %(levelname)7s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def initialize_addon(callback_url):
    # Splits callback into route selector and callback params and
    # patch sys.argv to emulate what is expected
    callback_url = callback_url if callback_url.startswith("plugin://") else "plugin://%s/" % callback_url
    scheme, pluginid, selector, params, fragment = urlparse.urlsplit(callback_url)
    sys.argv = (urlparse.urlunsplit([scheme, pluginid, selector, "", ""]), -1, "?%s" % params if params else "")

    # Fetch addon info
    addon_info = addon_db[pluginid]

    # Change to the addon directory
    os.chdir(addon_info.path)
    sys.path.insert(0, addon_info.path)
