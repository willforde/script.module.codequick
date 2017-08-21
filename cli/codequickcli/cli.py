# Standard Library Imports
from argparse import ArgumentParser
import logging
import sys

# Package imports
from codequickcli.interactive import interactive
from codequickcli import logger

# Create Parser to parse the required arguments
parser = ArgumentParser(description="Execute kodi plugin")
parser.add_argument("pluginid", help="The id of the plugin or a plugin path to run")
parser.add_argument("-l", "--logging", help="Show the logging output", action="store_true")
parser.add_argument("-p", "--preselect", help="A comma seporated list of pre selections", nargs=1)


def main(cli_args=sys.argv[1:]):
    # Parse the cli arguments
    args = parser.parse_args(cli_args)

    # Enable logging for debug messages if logging flag was given
    if args.logging:
        logger.setLevel(logging.DEBUG)

    # Convert any preselection into a list of selections
    preselect = map(int, args.preselect[0].split(",")) if args.preselect else None

    # Execute the addon in interactive mode
    interactive(args.pluginid, preselect)


if __name__ == "__main__":
    main()