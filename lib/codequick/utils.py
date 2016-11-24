# Kodi imports
import xbmc
import xbmcgui
from .support import logger, get_addon_data
from HTMLParser import HTMLParser
from xml.etree import ElementTree as ElementTree

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


class ETBuilder(HTMLParser):
    def __init__(self, tag=u"", attrs=None, wanted_tags=None, root_tag=None):
        """Initialize and reset this instance."""
        HTMLParser.__init__(self)
        self._in_sec = None if tag else True
        self._tree = ElementTree.TreeBuilder()
        self._search_tag = tag
        self._root_tag = root_tag

        # Make sure that wanted_tags is a list
        if wanted_tags is None:
            wanted_tags = []
        elif isinstance(wanted_tags, tuple):
            wanted_tags = list(wanted_tags)
        else:
            msg = "Wanted tags is not of type: tuple or list, %s" % type(wanted_tags)
            assert isinstance(wanted_tags, list), msg

        # Append the search tag to wanted tags so the parser can use it as the root tag
        if tag and wanted_tags and tag not in wanted_tags:
            wanted_tags.append(tag)

        # Split attributes into wanted and unwanted attributes
        self._unw_attrs = [attrs.pop(key) for key, value in attrs.items() if value is False] if attrs else []
        self._w_tags = wanted_tags
        self._w_attrs = attrs

    def run(self, html):
        # Set a root tag if givin
        if self._root_tag:
            self._tree.start(self._root_tag, {})

        # Parse the document
        try:
            self.feed(html)
        except EOFError:
            self.reset()

        # End the root tag if set
        if self._root_tag:
            self._tree.end(self._root_tag)

        # Close the _tree builder and return the root
        # tag that is returned by the treebuilder
        return self._tree.close()

    def handle_starttag(self, tag, attrs):
        # Search for requested section if required
        if tag == self._search_tag and self._check_attrs(attrs):
            self._in_sec = self._tree.start(tag, dict(attrs) if attrs else {})
            self._search_tag = u""

        # Build tree of requested element tags
        elif self._in_sec is not None and (not self._w_tags or tag in self._w_tags):
            self._tree.start(tag, dict(attrs) if attrs else {})

    def handle_endtag(self, tag):
        # Close current tree element for requested tags
        if self._in_sec is not None and (not self._w_tags or tag in self._w_tags):
            elem = self._close_tag(tag)
            if self._in_sec is elem:
                self._in_sec = None
                raise EOFError

    def handle_data(self, data):
        # Add tag data to element only if it contains text and not just an empty string with white spaces
        data = data.strip()
        if data and self._in_sec is not None and (not self._w_tags or self.lasttag in self._w_tags):
            self._tree.data(data)

    def _check_attrs(self, attrs):
        # If we have required attrs to match then search all attrs for wanted attrs
        # And also check that we do not have any attrs that are unwanted
        if attrs and (self._w_attrs or self._unw_attrs):
            wanted_attrs = self._w_attrs.copy()
            unwanted_attrs = self._unw_attrs
            for key, value in attrs:
                # Check for unwanted attrs
                if key in unwanted_attrs:
                    return False

                # Check for wanted attrs
                elif key in wanted_attrs:
                    c_value = wanted_attrs[key]
                    if c_value == value or c_value is True:
                        # Remove the attra form the wanted dict of attrs
                        # Indicates that this attr has been found
                        del wanted_attrs[key]

            # Check that wanted_attrs is empty sense empty means that all attrs ware found
            # Now the tag counter can start_time so to indicate that we are inside the requested tag
            if not wanted_attrs:
                return True

        # Start tag counter if requested tag is found and there is no attributes required
        elif not self._w_attrs:
            return True

    def _close_tag(self, tag):
        try:
            # Close the current tree element
            elem = self._tree.end(tag)

            # Check that the closed tag is whats expected
            if elem.tag == tag:
                return elem
            else:
                # Didn't find expected tag element. Must raise AssertionError sense the elementtree
                # treebuilder would normaly raise that error but it is silenly ignored in kodi
                raise AssertionError("end tag mismatch (expected %s, got %s)" % (elem.tag, tag))

        except AssertionError, e:
            str_error = str(e)
            logger.debug(str_error)
            if "end tag mismatch" in str_error:
                # Atempt to extract the expected tag and
                # check that it matches the last tag
                expected = str_error.replace("expected ", "").split("(")[-1].split(",")[0]
                if expected == self.lasttag:
                    return self._tree.end(tag)
                else:
                    raise
            else:
                raise
