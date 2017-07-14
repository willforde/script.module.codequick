# Standard Library Imports
import urlparse

# Kodi imports
import xbmc


def keyboard(heading, default="", hidden=False):
    """
    Return User input as a unicode string.

    :param heading: Keyboard heading.
    :type heading: str or unicode

    :param default: (Optional) Default text entry.
    :type default: str or unicode

    :param hidden: (Optional) True for hidden text entry.
    :type hidden: bool

    :return: The text that the user entered into text entry box.
    :rtype: unicode
    """
    # Convert input from unicode to string if required
    default = default.encode("utf8") if isinstance(default, unicode) else default
    heading = heading.encode("utf8") if isinstance(heading, unicode) else heading

    # Show the onscreen keyboard
    kb = xbmc.Keyboard(default, heading, hidden)
    kb.doModal()
    text = kb.getText()
    if kb.isConfirmed() and text:
        return unicode(text, "utf8")
    else:
        return u""


def parse_qs(qs):
    """
    Parse a urlencoded query string, and return the data as a dictionary.

    :param qs: Percent-encoded query string to be parsed.
    :type qs: str or unicode

    :return: Returns a dict of key/value pairs with the value as unicode.
    :rtype: dict

    :raises ValueError: If duplicate query field names exists.
    """
    params = {}
    for key, value in urlparse.parse_qsl(qs.encode("utf8") if isinstance(qs, unicode) else qs):
        if key not in params:
            params[key] = unicode(value, encoding="utf8")
        else:
            raise ValueError("encountered duplicate param field name: '{}'".format(key))

    return params
