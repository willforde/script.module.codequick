# Kodi imports
import xbmcaddon
import xbmc

# Package imports
from .logging import logger

__all__ = ["youtube_hd", "youtube_cache", "keyBoard", "get_skin_name", "strip_tags"]

def getAddonSetting(id, key):
	"""
	Return setting for selected addon
	
	id : string --- id of the addon that the module needs to access
	key : string --- id of the setting that the module needs to access
	"""
	return unicode(xbmcaddon.Addon(id).getSetting(key), "utf8")

def getAddonData(id, key):
	""" 
	Returns the value of an addon property as unicode
	
	id : string --- id of the addon that the module needs to access.
	key : string --- id of the property that the module needs to access.
	"""
	return unicode(xbmcaddon.Addon(id).getAddonInfo(key), "utf8")

def youtube_hd(default=0, limit=1):
	"""
	Return youtube quality setting as integer, 0 = SD, 1 = 720p, 2 = 1080p, 3 = 4k
	
	[default] : integer --- default value to return if unable to fetch quality setting. (default 0)
	[limit] : integer --- limit setting value to any one of the quality settings. (default 1)
	"""
	try: 
		value = getAddonSetting("plugin.video.youtube", "kodion.video.quality")
		setting = int(value)
	except:
		logger.debug("Unable to fetch youtube video qualit setting")
		return default
	else:
		if setting == 0: return None
		elif setting > 0 and setting <= 4:
			if setting > limit+1: return limit
			else: return setting - 1
		else:
			return default

def youtube_lang(lang=u"en"):
	"""
	Return the language set by the youtube addon
	
	[lang] : string or unicode --- The default language to use if no language was set in the youtube addon
	"""
	setting = getAddonSetting("plugin.video.youtube", "youtube.language")
	if setting:
		dash = setting.find(u"-")
		if dash > 0: return setting[:dash]
	return lang

def keyBoard(default="", heading="", hidden=False):
	"""
	Return User input as a unicode string
	
	[default] : string or unicode --- default text entry (default "")
	[heading] : string or unicode --- keyboard heading (default "")
	[hidden] : boolean --- True for hidden text entry (default False)
	"""
	kb = xbmc.Keyboard(default, heading, hidden)
	kb.doModal()
	text = kb.getText()
	if kb.isConfirmed() and text: return unicode(text, "utf8")
	else: return u""

def get_skin_name(skinID):
	""" Return name of giving skin ID """
	try: return getAddonData(skinID, "name")
	except:
		logger.debug("Unable to fetch skin name")
		return u"Unknown"

def strip_tags(html):
	""" Strips out html code and return plan text """
	sub_start = html.find(u"<")
	sub_end = html.find(u">")
	while sub_start < sub_end and sub_start > -1:
		html = html.replace(html[sub_start:sub_end + 1], u"").strip()
		sub_start = html.find(u"<")
		sub_end = html.find(u">")
	return html

def container_refresh():
	""" Refresh the Container listings """
	xbmc.executebuiltin("Container.Refresh")
