# Standard Library Imports
import urllib
import time
import abc
import os

# Kodi Imports
import xbmcplugin
import xbmcgui
import xbmc

# Package imports
from .api import Base, route, localized, cls_for_route

# Prerequisites
localized({"Select_playback_item":25006, "Related_Videos":32904, "Next_Page":33078, "Search":137, "Most_Recent":32903, "Youtube_Channel":32901})
_sortMethods = set((xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE,))
_sortAdd = _sortMethods.add
_listItem = xbmcgui.ListItem
_strptime = time.strptime
_strftime = time.strftime

class ListItem(_listItem):
	"""
	A wrapper for the xbmcgui.ListItem class witch adds extra methods
	to automate specific tasks to make using the ListItem API easier.
	"""
	
	def __init__(self):
		# Call Overridden init Method
		_listItem.__init__(self)
		
		# Set instance wide variables
		self._streamInfo = {"video": {}, "audio": {}}
		self._contextMenu = [self._refreshContext]
		self._infoLabels = {}
		self._imagePaths = {"fanart": self._fanart} if self._fanart else {}
		self._urlQuerys = {}
	
	def setLabel(self, lable):
		""" Sets label : string or unicode """
		_listItem.setLabel(self, lable)
		self._infoLabels["title"] = lable
		self._urlQuerys["title"] = lable.encode("ascii", "ignore")
	
	def setPlot(self, value):
		""" Set plot info : string or unicode """
		self._infoLabels["plot"] = value
	
	def setSize(self, value):
		""" Set size info : string digit or long integer """
		self._infoLabels["size"] = long(value)
		_sortAdd(xbmcplugin.SORT_METHOD_SIZE)
	
	def setGenre(self, value):
		""" Set genre info : string or unicode """
		self._infoLabels["genre"] = value
		_sortAdd(xbmcplugin.SORT_METHOD_GENRE)
	
	def setStudio(self, value):
		""" Set studio info : string or unicode """
		self._infoLabels["studio"] = value
		_sortAdd(xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
	
	def setCount(self, value):
		""" Set count info : integer as string or integer """
		self._infoLabels["count"] = int(value)
		_sortAdd(xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
	
	def setRating(self, value):
		""" Set rating info : Float as string or Float """
		self._infoLabels["rating"] = float(value)
		_sortAdd(xbmcplugin.SORT_METHOD_VIDEO_RATING)
	
	def setEpisode(self, value):
		""" Set episode info : integer as string or integer """
		self._infoLabels["episode"] = int(value)
		_sortAdd(xbmcplugin.SORT_METHOD_EPISODE)
	
	def setIcon(self, image):
		""" Set icon filename : string or unicode """
		self._imagePaths["icon"] = image
	
	def setFanart(self, image):
		""" Set fanart path : string or unicode """
		self._imagePaths["fanart"] = image
	
	def setPoster(self, image):
		""" Set poster path : string or unicode """
		self._imagePaths["poster"] = image
	
	def setBanner(self, image):
		""" Set banner path: string or unicode """
		self._imagePaths["banner"] = image
	
	def setClearArt(self, image):
		""" Set clearart path: string or unicode  """
		self._imagePaths["clearart"] = image
	
	def setClearLogo(self, image):
		""" Set clearlogo path: string or unicode """
		self._imagePaths["clearlogo"] = image
	
	def setLandscape(self, image):
		""" Set landscape image path: string or unicode """
		self._imagePaths["landscape"] = image
	
	def setArt(self, values):
		"""
		Sets the listitem's art
		
		values : dictionary --- pairs of { label: value }.
		"""
		self._imagePaths.update(values)
	
	def setThumb(self, image, local=0):
		"""
		Set thumbnail image path
		
		image : string or unicode --- Path to thumbnail image
		local : integer - (0/1/2) --- Changes image path to point to (Remote/Local/Global) paths
		
		>>> setThumb("http://youtube.com/youtube.png", 0)
		"http://youtube.com/youtube.png"
		
		>>> setThumb("youtube.png", 1)
		"special://home/addons/<addon_id>/resources/media/youtube.png"
		
		>>> setThumb("youtube.png", 2)
		"special://home/addons/script.module.xbmcutil/resources/media/youtube.png"
		"""
		if   local is 0: self._imagePaths["thumb"] = image
		elif local is 1: self._imagePaths["thumb"] = self._imageLocal % image
		elif local is 2: self._imagePaths["thumb"] = self._imageGlobal % image
	
	def setDate(self, date, dateFormat):
		""" 
		Sets Date Info Label
		
		date : string --- Date of list item
		dateFormat : string --- Format of date string for strptime conversion
		
		>>> setDate("17/02/16", "%d/%m/%y")
		17.02.2016
		"""
		convertedDate = _strptime(date, dateFormat)
		self._infoLabels["date"] = _strftime("%d.%m.%Y", convertedDate) # 01.01.2009
		self._infoLabels["aired"] = _strftime("%Y-%m-%d", convertedDate) # 2009-01-01
		self._infoLabels["year"] = _strftime("%Y", convertedDate)
		_sortAdd(xbmcplugin.SORT_METHOD_DATE)
	
	def setDuration(self, duration):
		"""
		Sets duration Info
		
		duration : string or unicode or integer,
		
		Duration can be an integer or an integer represented as string or unicode.
		It can also be a hour:minute:second (52:45) value represented as a string or unicode
		that will be converted to a numeric value.
		
		>>> setDuration(3165)
		3165
		
		>>> setDuration(u"3165")
		3165
		
		>>> setDuration(u"52:45")
		3165
		"""
		if isinstance(duration, basestring):
			if u":" in duration:
				# Split Time By Marker and Convert to Integer
				timeParts = duration.split(":")
				timeParts.reverse()
				duration = 0
				counter = 1
				
				# Multiply Each Time Delta Segment by it's Seconds Equivalent
				for part in timeParts: 
					duration += int(part) * counter
					counter *= 60
			else:
				# Convert to Interger
				duration = int(duration)
		
		# Set Duration
		self._infoLabels["duration"] = duration
		_sortAdd(xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
	
	def setResumePoint(self, startPoint, totalTime=None):
		"""
		Set Resume Point for Kodi to start playing video
		
		startPoint : string or unicode --- The starting point of the video as a numeric value
		[totalTime] : string or unicode --- The total time of the video, if not giving, totalTime will be the duration set in the infoLabels
		
		"""
		self.setProperty("totaltime", totalTime or str(self._streamInfo["video"].get("duration","1")))
		self.setProperty("resumetime", startPoint)
	
	def addStreamInfo(self, isHD=None, video_codec="h264", audio_codec="aac", audio_channels=2, language="en", aspect=0):
		"""
		Set Stream details like codec & resolutions
		
		[isHD]           : integer - Sets the HD/4K overlay flag, None = Unknown, 0 = SD, 1 = 720p, 2 = 1080p, 3 = 4k. (default None)
		[video_codec]    : string - codec that was used for the video. (default h264)
		[audio_codec]    : string - codec that was used for the audio. (default aac)
		[audio_channels] : integer - number of audio channels. (default 2)
		[language]       : string - language that the audio is in. (default en) (English)
		[aspect]         : float - the aspect ratio of the video as a float, eg 2.33 (21:9), 1.78 (16:9), 1.33 (4:3), (default 0)
		"""
		
		# Add audio details
		audio_info = self._streamInfo["audio"]
		audio_info["channels"] = audio_channels
		audio_info["language"] = language
		audio_info["codec"] = audio_codec
		
		# Add video details
		video_info = self._streamInfo["video"]
		if aspect: video_info["aspect"] = aspect
		video_info["codec"] = video_codec
		
		# Standard Definition
		if isHD == 0:
			video_info["width"] = 768
			video_info["height"] = 576
		
		# HD Ready
		elif isHD == 1:
			video_info["width"] = 1280
			video_info["height"] = 720
			video_info["aspect"] = 1.78
		
		# Full HD
		elif isHD == 2:
			video_info["width"] = 1920
			video_info["height"] = 1080
			video_info["aspect"] = 1.78
		
		# 4K
		elif isHD == 3:
			video_info["width"] = 3840
			video_info["height"] = 2160
			video_info["aspect"] = 1.78
	
	def menu_related(self, cls, **query):
		"""
		Adds a context menu item to link to related videos
		
		cls : Class --- Class that will be called by the related video context menu item
		[query] : keyword args --- keywords that will be passed to related video class
		"""
		if query:
			query.setdefault("updatelisting", "true")
			command = "XBMC.Container.Update(%s)" % cls.url_for_route(cls._route, query)
		else:
			command = "XBMC.Container.Update(%s?updatelisting=true)" % cls.url_for_route(cls._route)
		
		# Append Command to context menu
		self._contextMenu.append((self._strRelated, command))
	
	def menu_update(self, cls, label, **query):
		"""
		Adds a context menu item to link to related videos
		
		cls : Class --- Class that will be called by the related video context menu item
		label : string or unicode --- Title of the context menu item
		[query] : keyword args --- keywords that will be passed to giving class
		"""
		if query:
			query.setdefault("updatelisting", "true")
			command = "XBMC.Container.Update(%s)" % cls.url_for_route(cls._route, query)
		else:
			command = "XBMC.Container.Update(%s?updatelisting=true)" % cls.url_for_route(cls._route)
		
		# Append Command to context menu
		self._contextMenu.append((label, command))
	
	def __setitem__(self, key, value):
		self._urlQuerys[key] = value
	
	def update(self, _dict):
		self._urlQuerys.update(_dict)
	
	def __contains__(self, key):
		return key in self._urlQuerys
	
	def _get(self, path, type, isFolder, isplayable):
		"""
		Returns a tuple of listitem properties, (path, listitem, isFolder)
		
		path : string --- url of video or addon to send to kodi
		type : string --- Type of listitem content that will be send to kodi. Option are (video:audio)
		isFolder : boolean --- True if listing folder items else False for video items
		"""
		
		# Set Kodi InfoLabels
		self.setInfo(type, self._infoLabels)
		
		# Set streamInfo if found
		if self._streamInfo["video"]: _listItem.addStreamInfo(self, "video", self._streamInfo["video"])
		if self._streamInfo["audio"]: _listItem.addStreamInfo(self, "audio", self._streamInfo["audio"])
		
		if isFolder:
			# Change Kodi Propertys to mark as Folder
			self.setProperty("isplayable","false")
			self.setProperty("folder","true")
			
			# Set Kodi icon image if not already set
			if not "icon" in self._imagePaths: self._imagePaths["icon"] = "DefaultFolder.png"
		
		else:
			# Change Kodi Propertys to mark as Folder
			self.setProperty("isplayable","true" if isplayable else "false")
			self.setProperty("folder","false")
			
			# Set Kodi icon image if not already set
			if not "icon" in self._imagePaths: self._imagePaths["icon"] = "DefaultVideo.png"
			
			# Add Video Specific Context menu items
			self._contextMenu.append(("$LOCALIZE[13347]", "XBMC.Action(Queue)"))
			self._contextMenu.append(("$LOCALIZE[13350]", "XBMC.ActivateWindow(videoplaylist)"))
			
			# Increment vid counter for later guessing of content type
			VirtualFS._vidCounter += 1
		
		# Add Context menu items
		self.addContextMenuItems(self._contextMenu)
		
		# Set listitem art
		_listItem.setArt(self, self._imagePaths)
		
		# Return Tuple of url, listitem, isFolder
		return (path, self, isFolder)
	
	def get(self, cls, type="video"):
		"""
		Takes a class to route to and returns a tuple of listitem properties, (path, listitem, isFolder)
		
		cls : Class --- Class that will be called by the related video context menu item
		[type] : string --- Type of listitem content that will be send to kodi. Option are (video:audio) (default video)
		"""
		
		# Create path to send to Kodi
		path = cls.url_for_route(cls._route, self._urlQuerys)
		
		# Return Tuple of url, listitem, isFolder
		return self._get(path, type, cls._isFolder, cls._isplayable)
	
	def get_route(self, route, type="video"):
		"""
		Takes a route to a class and Returns a tuple of listitem properties, (path, listitem, isFolder)
		
		route : string --- Route that will be called by the related video context menu item
		[type] : string --- Type of listitem content that will be send to kodi. Option are (video:audio) (default video)
		"""
		cls = cls_for_route(route, raise_on_error=True)
		return self.get(cls, type)
	
	def get_direct(self, path, type="video"):
		"""
		Take a direct url for kodi to use and Returns a tuple of listitem properties, (path, listitem, isFolder)
		
		path : string --- url of video or addon to send to kodi
		[type] : string --- Type of listitem content that will be send to kodi. Option are (video:audio) (default video)
		"""
		
		# Return Tuple of url, listitem, isFolder
		return self._get(path, type, False, True)
	
	@classmethod
	def add_item(_cls, cls, label, url=None, thumbnail=None):
		"""
		Basic constructor to add a simple listitem
		
		cls : class --- Class that will be call to show recent results
		label : string or unicode --- Lable of Listitem
		[url] : dict --- Url params to pass to listitem
		[thumbnail] : string or unicode --- Thumbnail image of listitem
		"""
		listitem = _cls()
		listitem.setLabel(label)
		if thumbnail: listitem.setThumb(thumbnail)
		if url: listitem.update(url)
		return listitem.get(cls)
	
	@classmethod
	def add_next(_cls, url=None):
		"""
		A Listitem constructor for Next Page Item
		
		url: dict --- Dictionary containing url querys to control addon
		"""
		
		# Fetch current url query
		base_url = Base.copy()
		if url: base_url.update(url)
		base_url["updatelisting"] = "true"
		base_url["nextpagecount"] = int(base_url.get("nextpagecount",1)) + 1
		
		# Create listitem instance
		listitem = _cls()
		listitem.setLabel(u"[B]%s %i[/B]" % (Base.getLocalizedString("Next_Page"), base_url["nextpagecount"]))
		listitem.setThumb(u"next.png", 2)
		listitem.update(base_url)
		
		# Fetch current route and return
		route = Base._urlObject.path.lower() if Base._urlObject.path else "/"
		return listitem.get_route(route)
	
	@classmethod
	def add_search(_cls, cls, url, label=None):
		"""
		A Listitem constructor to add Saved Search Support to addon
		
		cls : class --- Class that will be farwarded to search dialog
		url : dict --- Dictionary containing url querys combine with search term
		label : string --- Lable of Listitem
		"""
		listitem = _cls()
		if label: listitem.setLabel("[B]%s[/B]" % label)
		else: listitem.setLabel("[B]%s[/B]" % Base.getLocalizedString("Search"))
		listitem.setThumb(u"search.png", 2)
		url["route"] = cls._route
		listitem.update(url)
		return listitem.get_route("/internal/SavedSearches")
	
	@classmethod
	def add_recent(_cls, cls, url=None, label=None):
		""" 
		A Listitem constructor to add Recent Folder to addon
		
		cls : class --- Class that will be call to show recent results
		url : dict --- Dictionary containing url querys to pass to Most Recent Class
		label : string --- Lable of Listitem
		"""
		listitem = _cls()
		if url: listitem.update(url)
		if label: listitem.setLabel(u"[B]%s[/B]" % label)
		else: listitem.setLabel(u"[B]%s[/B]" % Base.getLocalizedString("Most_Recent"))
		listitem.setThumb(u"recent.png", 2)
		return listitem.get(cls)
	
	@classmethod
	def add_youtube(_cls, contentID, label=None, enable_playlists=True, wideThumb=False):
		"""
		A Listitem constructor to add a youtube channel to addon
		
		contentID : string --- ID of Youtube channel or playlist to list videos for
		label : string --- Title of listitem - default (-Youtube Channel)
		enable_playlists : boolean --- Set to True to enable listing of channel playlists, (defaults True)
		wideThumb : boolean --- Set to True to use a wide thumbnail or False for normal thumbnail image (default False)
		"""
		listitem = _cls()
		if label: listitem.setLabel(u"[B]%s[/B]" % label)
		else: listitem.setLabel(u"[B]%s[/B]" % Base.getLocalizedString("Youtube_Channel"))
		if wideThumb: listitem.setThumb("youtubewide.png", 2)
		else: listitem.setThumb("youtube.png", 2)
		listitem["contentid"] = contentID
		listitem["enable_playlists"] = str(enable_playlists).lower()
		return listitem.get_route("/internal/youtube/playlist")


class Executer(Base):
	_isFolder = False
	_isplayable = False


class VirtualFS(Base):
	_isFolder = True
	_isplayable = False
	__listitem = None
	_vidCounter = 0
	
	@abc.abstractmethod
	def start(self):
		"""
		Abstractmethod thats required to be overridden by subclassing
		and is the starting point for the addon to load
		"""
		pass
	
	def finalize(self):
		"""
		Method used to execute commands after the endOfDirectory function as been called
		
		Handy for executing code that can slow down the loading of addons but witch
		is not directly depended on by the addon.
		
		Not to be called directly but to be overridden by subclassing
		
		e.g. Cleanup code or pre fetching of metadata
		"""
		pass
	
	def __init__(self):
		""" Initialize Virtual File System """
		listitems = self.start()
		self._send_to_kodi(listitems)
		
		# Call Finalize Method if Exists
		try: self.finalize()
		except Exception as e: self.error("Failed to execute finalize method, Reason: %s", e)
	
	@property
	def listitem(self):
		""" Return a custom kodi listitem object """
		if self.__listitem is not None: return self.__listitem
		else:
			ListItem._fanart = self.fanart
			ListItem._strRelated = self.getLocalizedString("Related_Videos")
			ListItem._imageLocal = os.path.join(self.path, u"resources", u"media", u"%s")
			ListItem._imageGlobal = os.path.join(self._path_global, u"resources", u"media", u"%s")
			ListItem._refreshContext = ("$LOCALIZE[184]", "XBMC.Container.Update(%s)" % self.url_for_current({"refresh":"true"}))
			self.__listitem = ListItem
			return ListItem
	
	def _send_to_kodi(self, listitems):
		""" Add Directory List Items to Kodi """
		if listitems:
			# Convert results from generator to list
			listitems = list(listitems)
			
			# Add listitems to  
			xbmcplugin.addDirectoryItems(self._handle, listitems, len(listitems))
			
			# Set Kodi Sort Methods
			_handle = self._handle
			_addSortMethod = xbmcplugin.addSortMethod
			for sortMethod in sorted(_sortMethods):
				_addSortMethod(_handle, sortMethod)
			
			# Guess Content Type and set View Mode
			isFolder = self._vidCounter < (len(listitems) / 2)
			#xbmcplugin.setContent(_handle, "files" if isFolder else "episodes")
			self._setViewMode("folder" if isFolder else "video")
		
		# End Directory Listings
		updateListing = u"updatelisting" in self and self[u"updatelisting"] == u"true"
		cacheToDisc = "cachetodisc" in self
		xbmcplugin.endOfDirectory(self._handle, bool(listitems), updateListing, cacheToDisc)
	
	def _setViewMode(self, mode):
		""" Returns selected View Mode setting if available """
		settingKey = "%s.%s.view" % (xbmc.getSkinDir(), mode)
		viewMode = self.getSetting(settingKey, True)
		if viewMode: xbmc.executebuiltin("Container.SetViewMode(%s)" % viewMode.encode("utf8"))


class PlayMedia(Base):
	""" Class to handle the resolving and playing of video urls """
	_isFolder = False
	_isplayable = True
	
	@abc.abstractmethod
	def resolve(self):
		"""
		Abstractmethod thats required to be overridden by subclassing
		and is the method thats called to resolve the video url
		"""
		pass
	
	def finalize(self):
		"""
		Method used to execute commands after the endOfDirectory function as been called
		
		Handy for executing code that can slow down the loading of addons but witch
		is not directly depended on by the addon.
		
		Not to be called directly but to be overridden by subclassing
		
		e.g. Cleanup code or pre fetching of metadata
		"""
		pass
	
	def __init__(self):
		# Instance Vars
		self.__headers = []
		self.__mimeType = self.get("mimetype")
		
		# Resolve Video Url
		resolved = self.resolve()
		self._send_to_kodi(resolved)
		
		# Call Finalize Method if Exists
		try: self.finalize()
		except Exception as e: self.error("Failed to execute finalize method, Reason: %s", e)
	
	def setMimeType(self, value):
		""" Set the mimeType of the video """
		if isinstance(value, unicode): value = value.encode("ascii")
		self.__mimeType = value
	
	def setUserAgent(self, useragent):
		""" Add a User Agent header to kodi request """
		if isinstance(useragent, unicode): useragent = useragent.encode("ascii")
		self.__headers.append("User-Agent=%s" % urllib.quote_plus(useragent))
	
	def setReferer(self, referer):
		""" Add a Referer header to kodi request """
		if isinstance(referer, unicode): referer = referer.encode("ascii")
		self.__headers.append("Referer=%s" % urllib.quote_plus(referer))
	
	def create_playlist(self, urls):
		"""
		Create playlist for kodi and returns back the first item of that playlist to play
		
		url : iterable --- set of urls that will be used in the creation of the playlist
		"""
		
		# Create Playlist
		playlist = xbmc.PlayList()
		firstItem = None
		
		# Loop each item to create playlist
		for count, url in enumerate(urls, 1):
			# Create Listitem
			listitem = _listItem()
			listitem.setLabel(u"%s Part %i" % (self[u"title"], count))
			if self.__mimeType: listitem.setMimeType(self.__mimeType)
			url = self._check_url(url)
			listitem.setPath(url)
			
			# Populate Playlis
			playlist.add(url, listitem)
			if firstItem is None: firstItem = listitem
		
		# Return first playlist item to send to kodi
		return firstItem
	
	def creat_loopback(self, url, **extra_params):
		"""
		Create a playlist where the second item loops back to current addon to load next video
		e.g. Party Mode
		
		url : string or unicode --- url for the first listitem in the playlist to use
		extra_params : kwargs --- extra params to add to the loopback request to access the next video
		"""
		
		# Create Playlist
		playlist = xbmc.PlayList()
		
		# Create Main listitem
		mainItem = _listItem()
		mainItem.setLabel(self[u"title"])
		if self.__mimeType: mainItem.setMimeType(self.__mimeType)
		url = self._check_url(url)
		mainItem.setPath(url)
		playlist.add(url, mainItem)
		
		# Create Loopback listitem
		loopItem = _listItem()
		loopItem.setLabel("Loopback")
		url = self.url_for_current(extra_params)
		loopItem.setPath(url)
		playlist.add(url, loopItem)
		
		# Return main listitem
		return mainItem
	
	def extract_source(self, url, quality=None):
		"""
		Extract video url using Youtube-DL
		
		url : string or unicode --- Url to fetch video for
		[quality] : integer --- Quality value to pass to StreamExtractor (default None)
		
		quality is 0=SD, 1=720p, 2=1080p, 3=4K
		"""
		import YDStreamExtractor
		videoInfo = YDStreamExtractor.getVideoInfo(url, quality)
		
		# If there is more than one stream found then ask for selection
		if videoInfo.hasMultipleStreams(): return self.source_selection(videoInfo)
		else: return videoInfo.streamURL()
	
	def source_selection(self, videoInfo):
		""" Ask user with video stream to play """
		displayList = ["%s - %s" % (stream["ytdl_format"]["extractor"].title(), stream["title"]) for stream in videoInfo.streams()]
		dialog = xbmcgui.Dialog()
		ret = dialog.select(self.getLocalizedString("Select_playback_item"), displayList)
		if ret >= 0:
			videoInfo.selectStream(ret)
			return videoInfo.streamURL()
		else:
			return None
	
	def _check_url(self, url):
		""" Check if there are any headers to add to url and return url and a string """
		if isinstance(url, unicode): url = url.encode("ascii")
		if self.__headers: url = "%s|%s" (url, "&".join(self.__headers))
		return url
	
	def _send_to_kodi(self, resolved):
		""" Construct playable listitem and send to kodi """
		
		# Use resoleved as is if its already a listitem
		if isinstance(resolved, _listItem): listitem = resolved
		
		# Create listitem object if resolved object is a basestring (string/unicode)
		elif isinstance(resolved, basestring):
			listitem = _listItem()
			if self.__mimeType: listitem.setMimeType(self.__mimeType)
			resolved = self._check_url(resolved)
			listitem.setPath(resolved)
		
		# No valid resolved value was found
		else: raise ValueError("Url resolver returned invalid Url: %r" % resolved)
		
		# Send playable listitem to kodi
		xbmcplugin.setResolvedUrl(self._handle, True, listitem)
	
	def youtube_video_url(self, videoid):
		"""
		Return url that redirects to youtube addon to play video
		
		videoid : string --- ID of the video to play
		"""
		return u"plugin://plugin.video.youtube/play/?video_id=%s" % videoid
	
	def youtube_playlist_url(self, playlistid, mode=u"normal"):
		"""
		Return url that redirects to youtube addon to play playlist
		
		playlistid : string or unicode --- Id of the playlist to play
		[mode] : string or unicode --- Order of the playlist, (normal/reverse/shuffle) (default normal)
		"""
		return u"plugin://plugin.video.youtube/play/?playlist_id=%s&mode=%s" % (playlistid, mode)


@route("/play/source")
class PlaySource(PlayMedia):
	""" Class to handle the resolving and playing of video urls using Youtube-DL to fetch video"""
	
	def resolve(self):
		""" Resolver that resolves video using Youtube-DL video extracter """
		return self.extract_source(self[u"url"])

# Import the extra module to register the routes
from . import extras
