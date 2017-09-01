# Standard Library Imports
import logging

# Package imports
from codequickcli import initialize_addon
from codequickcli.support import logger


def initialize(pluginid):
    """Setup codequickcli in testing mode."""

    # Only output warning messages to console
    logger.setLevel(logging.WARNING)

    # Initialize the addon and all it's dependencies
    initialize_addon(pluginid)
