# Kodi imports
import xbmc
import xbmcgui
from .support import logger, get_addon_data
from HTMLParser import HTMLParser
from xml.etree import ElementTree

__all__ = ["keyboard", "notification", "get_skin_name", "strip_tags", "requests_session"]


def keyboard(default="", heading="", hidden=False):
    """
    Return User input as a unicode string.

    Parameters
    ----------
    default : str, optional(default='')
        default text entry.

    heading : str, optional(default='')
        keyboard heading.

    hidden : bool, optional(default=False)
        True for hidden text entry.

    Returns
    -------
    unicode
        The text that the user entered into text entry box.

    Raises
    ------
    UnicodeError
        If unable to convert keyboard entry from utf8 to unicode.
    """
    kb = xbmc.Keyboard(default, heading, hidden)
    kb.doModal()
    text = kb.getText()
    if kb.isConfirmed() and text:
        return unicode(text, "utf8")
    else:
        return u""


def notification(heading, message, icon="info", display_time=5000, sound=True):
    """
    Send a notification to kodi

    Parameters
    ----------
    heading : bytestring
        Dialog heading.

    message : bytestring
        Dialog message.

    icon : bytestring, optional(default="info")
        Icon to use. option are 'error', 'info', 'warning'.

    display_time : bytestring, optional(default=5000)
        Display_time in milliseconds to show dialog.

    sound : bytestring, optional(default=True)
        Whether or not to play notification sound.
    """

    # Convert heading and messegs to UTF8 strings if needed
    if isinstance(heading, unicode):
        heading = heading.encode("utf8")
    if isinstance(message, unicode):
        message = message.encode("utf8")

    # Send Error Message to Display
    dialog = xbmcgui.Dialog()
    dialog.notification(heading, message, icon, display_time, sound)


def get_skin_name(skin_id):
    """
    Returns the name of given skin ID.

    Parameters
    ----------
    skin_id : str
        Id of the skin in witch to get the name of.

    Returns
    -------
    unicode
        The name of given skin, "Unknown" if failed to fetch proper name.
    """
    try:
        return get_addon_data(skin_id, "name")
    except (RuntimeError, UnicodeError) as e:
        logger.debug("Unable to fetch skin name")
        logger.debug(e)
        return u"Unknown"
