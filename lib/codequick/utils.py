# Standard Library Imports
from functools import partial
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


def extract_qs(qs, key):
    """
    Parse a urlencoded query string, and extract specified key.

    .. note:: qs can be either a query string or an absolute url with a query string.

    :type qs: str or unicode
    :param qs: Percent-encoded query string or absolute url to be parsed.
    :type key: str or unicode
    :param key: The key for the value to extract.

    :return: The requested value.
    :rtype: unicode

    :raises ValueError: If duplicate query field names exists.

    Example::

        vid = extract_qs("videoid=d26e5s8e&topic=video&page=1", "videoid")
        vid = extract_qs("http://example.com/playvideo?videoid=d26e5s8e&topic=video&page=1", "videoid")
    """
    if qs.startswith("http://") or qs.startswith("https://"):
        qs = urlparse.urlsplit(qs).query

    data = parse_qs(qs)
    return data[key]


def urljoin(base_url):
    """
    Join a base URL and a possibly relative URL to form an absolute
    interpretation of the latter.

    :type base_url: str or unicode
    :param base_url: The base url.
    :returns: A function that accepts a relative or absolute url and returns a full absolute url.
    """
    return partial(urlparse.urljoin, base_url)
