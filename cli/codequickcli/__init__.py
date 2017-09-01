# Standard Library Imports
import sys
import os

# Package imports
from codequickcli.addondb import db as addon_db
from codequickcli.support import urlparse


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
