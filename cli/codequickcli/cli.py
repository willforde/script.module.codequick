# -*- coding: utf-8 -*-

# Standard Library Imports
from argparse import ArgumentParser
import logging
import sys
import os

# Package imports
from codequickcli.interactive import interactive
from codequickcli.utils import safe_path, ensure_unicode
from codequickcli.support import logger

# Create Parser to parse the required arguments
parser = ArgumentParser(description="Execute kodi plugin")
parser.add_argument("pluginpath", help="The path to the plugin to execute. Path can be full or relative")
parser.add_argument("-l", "--logging", help="Show debug logging output", action="store_true")
parser.add_argument("-p", "--preselect", help="Comma separated list of pre selections", nargs=1)


def main(cli_args=sys.argv[1:]):
    # Parse the cli arguments
    args = parser.parse_args(cli_args)

    # Enable debug logging if logging flag was given
    if args.logging:
        logger.setLevel(logging.DEBUG)

    # Convert any preselection into a list of selections
    preselect = list(map(int, args.preselect[0].split(","))) if args.preselect else None

    # Execute the addon in interactive mode
    plugin_path = os.path.realpath(decode_arg(args.pluginpath))

    # Check if plugin actually exists
    if os.path.exists(safe_path(plugin_path)):
        interactive(plugin_path, preselect)

    # Check if we are already in the requested plugin directory if pluginpath was a plugin id
    elif args.pluginpath.startswith("plugin.") and os.path.basename(os.getcwd()) == args.pluginpath:
        plugin_path = ensure_unicode(os.getcwd(), sys.getfilesystemencoding())
        interactive(plugin_path, preselect)
    else:
        raise RuntimeError("unable to find requested add-on: {}".format(plugin_path.encode("utf8")))


def decode_arg(path):
    # Execute the addon in interactive mode
    if isinstance(path, bytes):
        try:
            # There is a possibility that this will fail
            return path.decode(sys.getfilesystemencoding())
        except UnicodeDecodeError:
            try:
                # Attept decoding using utf8
                return path.decode("utf8")
            except UnicodeDecodeError:
                # Fall back to latin-1
                return path.decode("latin-1")
                # If this fails then we are fucked
    else:
        return path


# This is only here for development
# Allows this script to be call directly
if __name__ == "__main__":
    main()
