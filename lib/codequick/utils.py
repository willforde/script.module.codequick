# Kodi imports
import xbmc
import xbmcgui
from .support import logger, get_addon_data
from HTMLParser import HTMLParser

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


def strip_tags(html):
    """
    Strips out html code and return plan text.

    Parameters
    ----------
    html : unicode
        HTML code that will be striped of html tags.

    Returns
    -------
    unicode
        Text with the html tags striped out.
    """
    sub_start = html.find(u"<")
    sub_end = html.find(u">")
    while sub_end > sub_start > -1:
        html = html.replace(html[sub_start:sub_end + 1], u"").strip()
        sub_start = html.find(u"<")
        sub_end = html.find(u">")
    return html


class SectionParser(HTMLParser):
    def __init__(self, tag_name=None, attrs=None):
        """ Initialize and reset this instance. """
        HTMLParser.__init__(self)
        self._search_tag = tag_name
        self._counter = 0

        # Split attributes into wanted an unwanted attributes
        self._unwanted_attrs = [attrs.pop(key) for key, value in attrs.items() if value is False]
        self._wanted_attrs = attrs

        self.start_pos = None
        self.end_pos = None

    def filter(self, html):
        # Parse the html to find the requested tag section start and end line numbers
        try:
            self.feed(html)
        except EOFError:
            pass

        # Filter down to only the lines that are requested
        filtered_lines = [line for count, line in enumerate(html.split("\n")) if
                          (self.start_pos[0] - 2) < count < self.end_pos[0]]

        # Strip out any unwanted text in the first and last line
        filtered_lines[0] = filtered_lines[0][self.start_pos[1]:]
        filtered_lines[-1] = filtered_lines[-1][:self.end_pos[1] + len("</%s>" % self._search_tag)]

        # Convert the filtered lines back into a unicode string
        return u"\n".join(filtered_lines)

    def handle_starttag(self, tag, attrs):
        if tag == self._search_tag:
            # Increment the tag counter to indicate that we are still inside the requested tag
            # When tag counter returns back to zero then we must be finished with that tag section
            if self._counter > 0:
                self._counter += 1

            # If we have required attrs to match then search all attrs for wanted attrs
            # And also check that we do not have any attrs that are unwanted
            elif attrs and (self._wanted_attrs or self._unwanted_attrs):
                wanted_attrs = self._wanted_attrs.copy()
                unwanted_attrs = self._unwanted_attrs
                for key, value in attrs:
                    # Check for unwanted attrs
                    if key in unwanted_attrs:
                        return None

                    # Check for wanted attrs
                    elif key in wanted_attrs:
                        c_value = wanted_attrs[key]
                        if c_value == value or c_value is True:
                            # Remove the attra form the wanted dict of attrs
                            # Indicates that this attr has been found
                            del wanted_attrs[key]

                # Check that wanted_attrs is empty sense empty means that all attrs ware found
                # Now the tag counter can start so to indicate that we are inside the requested tag
                if not wanted_attrs:
                    self._counter = 1
                    self.start_pos = self.getpos()

            # Start tag counter if requested tag is found and there is no attributes required
            elif not self._wanted_attrs:
                self._counter = 1
                self.start_pos = self.getpos()

    def handle_endtag(self, tag):
        if tag == self._search_tag:
            # When tag counter is already at 1 then we must be at the requested end tag so we must
            # raise EOFError to stop parsing anymore html
            if self._counter == 1:
                self.end_pos = self.getpos()
                raise EOFError

            # We must not yet be at the end of the requested tag
            # So just decrement the tag counter
            else:
                self._counter -= 1
