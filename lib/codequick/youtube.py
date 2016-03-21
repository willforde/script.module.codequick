# Standard Library Imports
import os

# Package imports
from .inheritance import VirtualFS, PlayMedia
from .api import route, localized
from . import json

# Prerequisites
localized({"Go_to_channel":32902, "Playlists":136, "All_videos":16100})


@route("/internal/youtube/playlist")
class YTPlaylist(VirtualFS):
	""" List all videos in a playlist """
	def start(self):
		Gdata = APIControl(self)
		if "playlistid" in self: return Gdata.playlist(playlistID=self[u"playlistid"])
		else: return Gdata.playlist(contentID=self[u"contentid"])


@route("/internal/youtube/playlists")
class YTPlaylists(VirtualFS):
	""" List all the playlists of a channel """
	def start(self):
		if "channelid" in self: return self._initiate(channelID=self[u"channelid"])
		else: return self._initiate(contentID=self[u"contentid"])
	
	def _initiate(self, contentID=None, channelID=None):
		Gdata = APIControl(self)
		return list(Gdata.playlists(contentID, channelID))


@route("/internal/youtube/related")
class YTRelated(VirtualFS):
	""" List all videos that are related to a video id """
	def start(self):
		Gdata = APIControl(self)
		return Gdata.related(self[u"videoid"])


@route("/internal/youtube/play/video")
class PlayYTVideo(PlayMedia):
	""" Class to construct playable youtube video url """
	def resolve(self):
		return self.youtube_video_url(self[u"videoid"])


@route("/internal/youtube/play/playlist")
class PlayYTPlaylist(PlayMedia):
	""" Class to construct playable youtube playlist url """
	def resolve(self):
		return self.youtube_playlist_url(self[u"playlistid"], self.get(u"mode", u"normal"))


class YoutubeBase(YTPlaylists):
	"""
	Class to allow addons to just use youtube as the base
	
	Designed to be sub classed by addon to list all the available playlists for
	channel, as well as linking the the channels uploads, shown as "All Videos"
	
	To use the class just create a new class and inherit from this class
	and create required method that will return the Channel Name, channel ID
	
	contentID : string or unicode --- Channel ID or Channel Name to list playlists for, usefull when unsure of the type
	channelID : string or unicode --- ID of the channel to list playlists for when the channel ID is known
	
	Can create any one of the 2 methods, but if both are giving then channelID has priority
	-------------------------------------------
	@codequick.route("/")
	class Root(codequick.youtube.asAddon):
		def channelID(self):
			return "UCnavGPxEijftXneFxk28srA"
	"""
	
	def start(self):
		if hasattr(self, "channelID"):
			channelID = self.channelID()
			results = self._initiate(channelID=channelID)
			results.append(self.listitem.add_youtube(channelID, label=self.getLocalizedString("All_videos"), enable_playlists=False, wideThumb=True))
		elif hasattr(self, "contentID"):
			contentID = self.contentID()
			results = self._initiate(contentID=contentID)
			results.append(self.listitem.add_youtube(contentID, label=self.getLocalizedString("All_videos"), enable_playlists=False, wideThumb=True))
		else:
			raise ValueError("No Content ID was set for addon to work")
		
		return results


class APIControl(object):
	""" Class to control the access to the youtube API """
	
	__video_data = __channel_data = __category_data = None
	
	def __del__(self):
		""" Trim down the cache if cache gets too big """
		
		# Fetch data caches
		if not self.__video_data or not self.__channel_data: return None
		video_cache = self.__video_data
		channel_cache = self.__channel_data
		forceSync = False
		
		# Cut down the size of the video cache if it get larger than 2000 items
		cache_len = len(video_cache)
		remove_count = cache_len - 500
		if cache_len > 2000:
			self.base.debug("Running Youtube Cache Cleanup")
			video_cache.writeback = True
			for count, data in enumerate(sorted(((videoID, data[u"snippet"][u"publishedAt"]) for videoID, data in video_cache.iteritems()), key=lambda data: data[1])):
				if count < remove_count:
					del video_cache[data[0]]
				else:
					break
			
			# Remove any channel cache item that no longer referenced by the video cache
			if len(channel_cache) > 10:
				channelsLeft = {data[u"snippet"][u"channelId"] for data in video_cache.itervalues()}
				for channelID in channel_cache.keys():
					if not channelID in channelsLeft:
						del channel_cache[channelID]
						forceSync = True
				
		# Synchronize data to disk if needed and close connection to file
		channel_cache.close(forceSync)
		video_cache.close()
	
	def __init__(self, base):
		self.base = base
		req_session = base.request_basic(60*4)
		language = base.utils.youtube_lang(u"en")
		self.api = API(req_session, lang=language)
	
	@property
	def _category_data(self):
		""" Return opened category_data database or connect to the category_data database and return """
		if self.__category_data is not None: return self.__category_data
		else:
			dirPath = os.path.join(self.base._profile_global, "youtube")
			category_data = self.base.dictStorage("category_data.json", custom_dir=dirPath)
			self.__category_data = category_data
			return category_data
	
	@property
	def _channel_data(self):
		""" Return opened channel_data database or connect to the channel_data database and return """
		if self.__channel_data is not None: return self.__channel_data
		else:
			dirPath = os.path.join(self.base.profile, "youtube")
			channel_data = self.base.dictStorage("channel_data.json", custom_dir=dirPath)
			self.__channel_data = channel_data
			return channel_data
	
	@property
	def _video_data(self):
		""" Return opened video_data database or connect to the video_data database and return """
		if self.__video_data is not None: return self.__video_data
		else:
			dirPath = os.path.join(self.base.profile, "youtube")
			video_data = self.base.shelfStorage("video_data.shelf", custom_dir=dirPath)
			self.__video_data = video_data
			return video_data
	
	def _check_contentID(self, contentID, returnPlaylistID=True):
		"""
		Check the type of contentID we have and return the required ID for wanted type
		
		contentID : string or unicode --- ID of Youtube content to add, Channel Name, Channel ID, Channel Uploads ID or Playlist ID
		[returnPlaylistID] : boolean --- True to return a playlistID/uploadID or False for channelID (default True)
		"""
		
		# Fetch the channel cache object
		channel_data = self._channel_data
		
		# Return if content is a playlistID or uploadsID
		if contentID[:2] == "UU" or contentID[:2] == "PL":
			if returnPlaylistID: return contentID
			else: raise ValueError("ContentID is not a valid ID for wanted type: %s" % contentID)
		
		# If channel id then either return it or fetch the playlistID for channel
		elif contentID[:2] == "UC":
			if not returnPlaylistID: return contentID
			else:
				if not contentID in channel_data: self.update_channel_cache(id=contentID)
				return channel_data[contentID]["playlistID"]
		
		# ContentID must be a channel name so fetch the channelID and uploadsID
		else:
			channelID = self.base.getSetting(contentID)
			if not channelID or (returnPlaylistID and not channelID in channel_data):
				channelID = self.update_channel_cache(forUsername=contentID)
				if not channelID: self.base.setSetting(contentID, channelID)
			
			if returnPlaylistID: return channel_data[channelID]["playlistID"]
			else: return channelID
	
	def update_channel_cache(self, id=None, forUsername=None):
		"""
		Update on disk cache of channel information
		
		id : list or string or unicode --- ID of the channel for requesting infomation for.
		forUsername : string or unicode --- Username of the channel for requesting information for.
		"""
		
		# Fetch cache object
		channel_data = self._channel_data
		
		# Connect to API server and Fetch response
		feed = self.api.Channels(id, forUsername)
		
		# Update the cache Title, Description, playlistID and fanart
		for item in feed[u"items"]:
			title = item[u"snippet"][u"localized"][u"title"]
			description = item[u"snippet"][u"localized"][u"description"]
			playlistID = item[u"contentDetails"][u"relatedPlaylists"][u"uploads"]
			if u"brandingSettings" in item: fanart = item[u"brandingSettings"][u"image"][u"bannerTvMediumImageUrl"]
			else: fanart = None
			channel_data[item[u"id"]] = {"title":title, "description":description, "playlistID":playlistID, "fanart":fanart}
		
		# Sync cache to disk
		channel_data.sync()
		
		# Return the Channel ID of the first item, needed when using forUsername
		if forUsername: return feed[u"items"][0][u"id"]
		else: return None
	
	def update_category_cache(self, id=None):
		"""
		Update on disk cache of category information
		
		[id] : list or string or unicode --- ID(s) of the categories to fetch category names for. (default None)
		"""
		
		# Fetch category Information
		feed = self.api.VideoCategories(id)
		
		# Update category cache
		category_data = self._category_data
		for item in feed[u"items"]: category_data[item[u"id"]] = item[u"snippet"][u"title"]
		category_data.sync()
	
	def update_video_cache(self, id):
		"""
		Update on disk cache of video information
		
		id : list or string or unicode --- ID(s) of videos to fetch information for
		"""
		
		# Fetch video information
		video_database = self._video_data
		category_data = self._category_data
		feed = self.api.Videos(id)
		
		# Add data to cache
		check_categories = True
		for video in feed[u"items"]:
			video_database[video["id"]] = video
			if check_categories and not video["snippet"]["categoryId"] in category_data:
				self.update_category_cache()
				check_categories = False
	
	def playlists(self, contentID=None, channelID=None):
		"""
		List all playlist for giving channel
		
		[contentID] : string or unicode --- Channel ID or Channel Name to list playlists for, usefull when unsure of the type
		[channelID] : string or unicode --- ID of the channel to list playlists for when the channel ID is known
		
		Can pass in any one of the 2 arguments, but if both are giving then channelID has priority
		"""
		
		# Fetch channel ID
		if contentID: channelID = self._check_contentID(contentID, returnPlaylistID=False)
		elif not channelID: raise ValueError("No valid argument giving for youtube:playlists")
		feed = self.api.Playlists(channelID)
		
		# Fetch data caches
		channel_cache = self._channel_data
		if channelID in channel_cache: fanart = channel_cache[channelID]["fanart"]
		else: fanart = None
		
		# Loop Entries
		listitem = self.base.listitem
		for playlist in feed[u"items"]:
			# Create listitem object
			item = listitem()
			
			# Fetch Video ID
			item["playlistid"] = playlist[u"id"]
			
			# Fetch video snippet
			snippet = playlist[u"snippet"]
			
			# Fetch Title and Video Cound for combining Title
			item.setLabel(u"%s (%s)" % (snippet[u"localized"][u"title"], playlist[u"contentDetails"][u"itemCount"]))
			
			# Fetch Image Url
			item.setThumb(snippet[u"thumbnails"][u"medium"][u"url"])
			
			# Set Fanart
			if fanart: item.setFanart(fanart)
			
			# Fetch Possible Plot and Check if Available
			item.setPlot(snippet[u"localized"][u"description"])
			
			# Fetch Possible Date and Check if Available
			date = snippet[u"publishedAt"]
			item.setDate(date[:date.find("T")], "%Y-%m-%d")
			
			# Add InfoLabels and Data to Processed List
			yield item.get(YTPlaylist)
	
	def related(self, videoID):
		"""
		Search for all videos related to a giving video id
		
		videoID : string or unicode --- ID of the video to fetch related video for
		"""
		
		# Fetch search results
		feed = self.api.Search(self.base.get("pagetoken"), relatedToVideoId=videoID)
		videoList = [(video[u"snippet"][u"channelId"], video[u"id"][u"videoId"]) for video in feed["items"]]
		return self._videos(videoList, feed.get(u"nextPageToken"))
	
	def playlist(self, contentID=None, playlistID=None):
		"""
		List all video within youtube playlist
		
		[contentID] : string or unicode --- Channel ID / Channel Name or Playlist ID to list videos for, usefull when unsure of the type
		[playlistID] : string or unicode --- ID of the channel to list videos for when the playlist ID is known
		
		Can pass in any one of the 2 arguments, but if both are giving then playlistID has priority
		"""
		
		# Connect to API server and Fetch response
		if contentID: playlistID = self._check_contentID(contentID, returnPlaylistID=True)
		elif not playlistID: raise ValueError("No valid argument giving for youtube:playlist")
		feed = self.api.PlaylistItems(playlistID, self.base.get("pagetoken"))
		videoList = [(item[u"snippet"][u"channelId"], item[u"snippet"][u"resourceId"][u"videoId"]) for item in feed[u"items"] if item[u"status"][u"privacyStatus"] == u"public"]
		return self._videos(videoList, feed.get(u"nextPageToken"))
	
	def _videos(self, videoIDs, pagetoken=None):
		""" Process VideoIDs and return listitems in a generator """
		
		# Check if videoIDs is a valid list
		if not videoIDs: raise ValueError("No valid list of video IDs ware giving")
		
		# Fetch data caches
		video_cache = self._video_data
		category_cache = self._category_data
		channel_cache = self._channel_data
		
		# Check for any missing data
		channelIDs = set()
		fetchVideos = set()
		fetchChannels = set()
		for channelID, videoId in videoIDs:
			if not channelID in channel_cache: fetchChannels.add(channelID)
			if not videoId in video_cache: fetchVideos.add(videoId)
			channelIDs.add(channelID)
		
		# Fetch any missing data
		if fetchChannels: self.update_channel_cache(id=fetchChannels)
		if fetchVideos: self.update_video_cache(fetchVideos)
		
		# Fetch Youtube Video Quality Setting
		isHD = self.base.utils.youtube_hd(default=2)
		
		# Process Videos
		localInt = int
		listitem = self.base.listitem
		reFind = __import__("re").findall
		isRelated = str(u"videoid" in self.base).lower()
		for channelID, videoId in videoIDs:
			# Fetch Required Information
			videoData = video_cache[videoId]
			channelData = channel_cache[channelID]
			
			# Fetch video snippet & contentDetails
			snippet = videoData[u"snippet"]
			contentDetails = videoData[u"contentDetails"]
			
			# Create listitem object
			item = listitem()
			
			# Add channel Fanart
			if channelData["fanart"]: item.setFanart(channelData["fanart"])
			
			# Fetch video Image url
			item.setThumb(snippet[u"thumbnails"][u"medium"][u"url"])
			
			# Fetch Title
			item.setLabel(snippet[u"localized"][u"title"])
			
			# Fetch Description
			item.setPlot(snippet[u"localized"][u"description"])
			
			# Fetch Studio
			item.setStudio(snippet[u"channelTitle"])
			
			# Fetch Possible Date
			date = snippet[u"publishedAt"]
			item.setDate(date[:date.find("T")], "%Y-%m-%d")
			
			# Fetch Viewcount
			item.setCount(videoData[u"statistics"][u"viewCount"])
			
			# Fetch Category
			catID = snippet[u"categoryId"]
			if catID in category_cache: item.setGenre(category_cache[catID])
			
			# Set Quality and Audio Overlays
			if isHD >= 1 and contentDetails[u"definition"] == u"hd": item.addStreamInfo(isHD)
			else: item.addStreamInfo(0)
			
			# Fetch Duration
			durationStr = contentDetails[u"duration"]
			durationStr = reFind("(\d+)(\w)", durationStr)
			if durationStr:
				duration = 0
				for time, timeType in durationStr:
					if   timeType == "H": duration += (localInt(time) * 3600)
					elif timeType == "M": duration += (localInt(time) * 60)
					elif timeType == "S": duration += (localInt(time))
				
				# Set duration
				item.setDuration(duration)
			
			# Add Context item to link to related videos
			item.menu_related(YTRelated, videoid=videoId, updatelisting=isRelated)
			if len(channelIDs) > 1: item.menu_update(YTPlaylist, "Go to: %s" % snippet[u"channelTitle"], contentID=channelID)
			
			# Add InfoLabels and Data to Processed List
			yield item.get_direct(u"plugin://plugin.video.youtube/play/?video_id=%s" % videoData[u"id"])
		
		# Add next Page entry if pagetoken is giving
		if pagetoken:
			params = self.base.copy()
			params["pagetoken"] = pagetoken
			yield self.base.listitem.add_next(params)
		
		# Add playlists item to results
		if len(channelIDs) == 1 and not u"pagetoken" in self.base and self.base.get(u"enable_playlists",u"false") == u"true":
			item = listitem()
			item.setLabel(u"[B]%s[/B]" % self.base.getLocalizedString("Playlists"))
			item.setIcon("DefaultVideoPlaylists.png")
			item.setThumb(u"youtube.png", 2)
			item["channelid"] = list(channelIDs)[0]
			yield item.get(YTPlaylists)


class API(object):
	"""
	API class to handle requests to the youtube v3 api
	
	req_session : object --- Requests session object to handle the api requests
	"""
	def __init__(self, req_session, lang="en", maxResults="50", prettyPrint="false", key="AIzaSyCR4bRcTluwteqwplIC34wEf0GWi9PbSXQ"):
		# Setup Instance vars
		self.language = lang
		self.req_session = req_session
		self.default_params = {"maxResults":maxResults, "prettyPrint":prettyPrint, "key":key}
	
	def _connect_v3(self, type, params, max_age=None):
		"""
		Send API request and return response as a json object
		
		type : string or unicode --- Type of API resource to fetch
		params : dict --- The parameters to use in the request
		"""
		
		# Check type of video id(s) before making request
		if "id" in params and (isinstance(params["id"], list) or isinstance(params["id"], set)): params["id"] = u",".join(params["id"])
		
		url = "https://www.googleapis.com/youtube/v3/%s" % type
		source = self.req_session.get(url, params=params, headers={"X-Max-Age":max_age} if max_age else None)
		response = json.loads(source.content, encoding=None)#encoding=source.encoding)
		if not u"error" in response: return response
		else:
			try: message = response[u"error"]["errors"][0][u"message"]
			except: raise RuntimeError("Youtube V3 API return and error response")
			else: raise RuntimeError("Youtube V3 API return and error response: %s" % message)
	
	def Channels(self, id=None, forUsername=None):
		"""
		Return all available information for giving channel
		
		id : list or string or unicode --- ID of the channel for requesting infomation for.
		forUsername : string or unicode --- Username of the channel for requesting information for.
		
		NOTE:
		Argument must be either id or forUsername but not both.
		If both are giving then id will be used over forUsername.
		"""
		
		# Set parameters
		params = self.default_params.copy()
		params["fields"] = u"items(id,brandingSettings/image/bannerTvMediumImageUrl,contentDetails/relatedPlaylists/uploads,snippet/localized)"
		params["part"] = u"contentDetails,brandingSettings,snippet"
		params["hl"] = self.language
		
		# Add the id or channel name of the channel to params
		if id: params["id"] = id
		elif forUsername: params["forUsername"] = forUsername
		else: raise ValueError("No valid Argument was giving for channels")
		
		# Connect to server and return json response
		return self._connect_v3("channels", params)
	
	def VideoCategories(self, id=None, regionCode="us"):
		"""
		Return the categorie names for giving id(s)
		
		[id] : list or string or unicode --- ID(s) of the categories to fetch category names for. (default None)
		[regionCode] : string or unicode --- the region code for the categories ids (default us)
		
		If no id(s) are giving then all category ids are fetched for giving region that will default to US
		"""
		
		# Set parameters
		params = self.default_params.copy()
		params["fields"] = u"items(id,snippet/title)"
		params["part"] = u"snippet"
		params["hl"] = self.language
		params["regionCode"] = regionCode
		
		# Set mode of fetching, by id or region
		if id: params["id"] = id
		
		# Fetch video Information
		return self._connect_v3("videoCategories", params)
	
	def PlaylistItems(self, playlistId, pagetoken=None):
		"""
		Return all videos ids for giving playlist ID
		
		playlistId : string or unicode --- ID of Youtube playlist
		pagetoken : string or unicode --- The token for the next page of results
		"""
		
		# Set parameters
		params = self.default_params.copy()
		params["fields"] = u"nextPageToken,items(snippet(channelId,resourceId/videoId),status/privacyStatus)"
		params["part"] = u"snippet,status"
		params["playlistId"] = playlistId
		
		# Add pageToken if exists
		if pagetoken: params["pageToken"] = pagetoken
		
		# Connect to server and return json response
		return self._connect_v3("playlistItems", params)
	
	def Videos(self, id):
		"""
		Return all available information for giving video/vidoes
		
		id : list or string or unicode --- Video id(s) to fetch infomation for
		"""
		
		# Set parameters
		params = self.default_params.copy()
		params["fields"] = u"items(id,snippet(publishedAt,channelId,thumbnails/medium/url,channelTitle,categoryId,localized),contentDetails(duration,definition),statistics/viewCount)"
		params["part"] = u"contentDetails,statistics,snippet"
		params["hl"] = self.language
		params["id"] = id
		
		# Connect to server and return json response
		return self._connect_v3("videos", params)
	
	def Playlists(self, channelID):
		"""
		Return all playlist for a giving channelID
		
		channelID : string or unicode --- Id of the channel to fetch playlists for
		"""
		
		# Set Default parameters
		params = self.default_params.copy()
		params["fields"] = u"nextPageToken,items(id,contentDetails/itemCount,snippet(publishedAt,localized,thumbnails/medium/url))"
		params["part"] = u"snippet,contentDetails"
		params["channelId"] = channelID
		
		# Connect to server and return json response
		feed = self._connect_v3("playlists", params, 60*8)
		pagetoken = feed.get(u"nextPageToken")
		
		# Loop all pages
		while pagetoken:
			params[u"pageToken"] = pagetoken
			nextFeed = self._connect_v3("playlists", params)
			feed[u"items"].extend(nextFeed[u"items"])
			pagetoken = nextFeed.get(u"nextPageToken")
		
		# Return all Playlists
		feed[u"nextPageToken"] = None
		return feed
	
	def Search(self, pagetoken=None, **search_params):
		"""
		Return any search results
		
		pagetoken : string or unicode --- The token for the next page of results
		[search_params] : dict --- Youtube Data API Search Parameters, refer to "https://developers.google.com/youtube/v3/docs/search/"
		"""
		
		# Set Default parameters
		params = self.default_params.copy()
		params["fields"] = u"nextPageToken,items(id/videoId,snippet/channelId)"
		params["relevanceLanguage"] = self.language
		params["safeSearch"] = u"none"
		params["part"] = u"snippet"
		params["type"] = u"video"
		params.update(search_params)
		
		# Add pageToken if needed
		if pagetoken: params["pageToken"] = pagetoken
		
		# Connect to server and return json response
		return self._connect_v3("search", params)
