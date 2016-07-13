# Kodi imports
import xbmcaddon
import xbmc

# Package imports
from .api import logger

__all__ = ["youtube_hd", "youtube_cache", "keyBoard", "get_skin_name", "strip_tags"]


def get_addon_setting(addon_id, key):
    """
    Return setting for selected addon.

    Parameters
    ----------
    addon_id: str
        Id of the addon that contains the required setting.
    key : str
        Id of the required setting.

    Returns
    -------
    unicode
        setting from specified addon.

    Raises
    ------
    RuntimeError
        If given addon id was not found.
    UnicodeError
        If unable to convert property from utf8 to unicode.
    """
    return unicode(xbmcaddon.Addon(addon_id).getSetting(key), "utf8")


def get_addon_data(addon_id, key):
    """
    Returns the value of an addon property as unicode.

    Parameters
    ----------
    addon_id : str
        Id of the addon that contains the required value.
    key : str
        Id of the required property.

    Returns
    -------
    unicode
        The required property of requested addon.

    Raises
    ------
    RuntimeError
        If given addon id was not found.
    UnicodeError
        If unable to convert property from utf8 to unicode.
    """
    return unicode(xbmcaddon.Addon(addon_id).getAddonInfo(key), "utf8")


def youtube_hd(default=0, limit=1):
    """
    Return youtube quality setting as integer.

    Parameters
    ----------
    default : int, optional(default=0)
        default value to return if unable to fetch quality setting.
    limit : int, optional(default=1)
        limit setting value to any one of the quality settings.

    Returns
    -------
    int
        youtube quality setting as integer.

        0 = 480p
        1 = 720p
        2 = 1080p
        3 = 4k
    """
    try:
        quality = int(get_addon_setting("plugin.video.youtube", "kodion.video.quality"))
        ask = get_addon_setting("plugin.video.youtube", "kodion.video.quality.ask") == "true"
    except (RuntimeError, ValueError) as e:
        logger.error("Unable to fetch youtube video quality setting")
        logger.error(e)
        return default
    else:
        if ask is True:
            return 1
        elif quality < 3:
            return 0
        else:
            if quality > limit + 2:
                return limit
            else:
                return quality - 2


def youtube_lang(lang=u"en"):
    """
    Return the language set by the youtube addon.

    Parameters
    ----------
    lang : unicode, optional(default=u'en')
        The default language to use if no language was set.

    Returns
    -------
    unicode
        The language to use when fetching youtube content.
    """
    try:
        setting = get_addon_setting("plugin.video.youtube", "youtube.language")
    except (RuntimeError, UnicodeDecodeError):
        return unicode(lang)
    else:
        if setting:
            dash = setting.find(u"-")
            if dash > 0:
                return setting[:dash]

        return unicode(lang)


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


def container_refresh():
    """ Refresh the Container listings """
    xbmc.executebuiltin("Container.Refresh")
