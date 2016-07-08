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
from .api import Base, route, localized, cls_for_route, logger

# Prerequisites
localized({"Select_playback_item": 25006, "Related_Videos": 32904, "Next_Page": 33078,
           "search": 137, "Most_Recent": 32903, "Youtube_Channel": 32901, "Default": 571, "Enter_number": 611,
           "Custom": 636, "Remove": 1210, "Enter_search_string": 16017})

_sortMethods = {xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE}
_sortAdd = _sortMethods.add
_listItem = xbmcgui.ListItem
_strptime = time.strptime
_strftime = time.strftime


class ListItem(_listItem):
    """
    A wrapper for the xbmcgui.ListItem class witch adds extra methods
    to automate specific tasks to make using the ListItem API easier.
    """

    _refreshContext = None
    _imageLocal = None
    _fanart = None
    _strRelated = None
    _imageGlobal = None
    _sort_map = {"size": (xbmcplugin.SORT_METHOD_SIZE, long),
                 "genre": (xbmcplugin.SORT_METHOD_GENRE, None),
                 "studio": (xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE, int),
                 "count": (xbmcplugin.SORT_METHOD_PROGRAM_COUNT, None),
                 "rating": (xbmcplugin.SORT_METHOD_VIDEO_RATING, float),
                 "episode": (xbmcplugin.SORT_METHOD_EPISODE, int)}

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

    def info(self, key, value):
        try:
            sort_type, type_obj = self._sort_map[key]
        except KeyError:
            self._infoLabels[key] = value
        else:
            if type_obj:
                value = type_obj(value)
            self._infoLabels[key] = value
            _sortAdd(sort_type)

    def set_icon(self, image):
        """ Set icon filename : string or unicode """
        self._imagePaths["icon"] = image

    def set_fanart(self, image):
        """ Set fanart path : string or unicode """
        self._imagePaths["fanart"] = image

    def set_poster(self, image):
        """ Set poster path : string or unicode """
        self._imagePaths["poster"] = image

    def set_banner(self, image):
        """ Set banner path: string or unicode """
        self._imagePaths["banner"] = image

    def set_clear_art(self, image):
        """ Set clearart path: string or unicode  """
        self._imagePaths["clearart"] = image

    def set_clear_logo(self, image):
        """ Set clearlogo path: string or unicode """
        self._imagePaths["clearlogo"] = image

    def set_landscape(self, image):
        """ Set landscape image path: string or unicode """
        self._imagePaths["landscape"] = image

    def setArt(self, values):
        """
        Sets the listitem's art

        values : dictionary --- pairs of { label: value }.
        """
        self._imagePaths.update(values)

    def set_thumb(self, image, local=0):
        """
        Set thumbnail image path

        image : string or unicode --- Path to thumbnail image
        local : integer - (0/1/2) --- Changes image path to point to (Remote/Local/Global) paths

        >>> item = ListItem()
        >>> item.set_thumb("http://youtube.com/youtube.png", 0)
        "http://youtube.com/youtube.png"

        >>> item.set_thumb("youtube.png", 1)
        "special://home/addons/<addon_id>/resources/media/youtube.png"

        >>> item.set_thumb("youtube.png", 2)
        "special://home/addons/script.module.xbmcutil/resources/media/youtube.png"
        """
        if local is 0:
            self._imagePaths["thumb"] = image
        elif local is 1:
            self._imagePaths["thumb"] = self._imageLocal % image
        elif local is 2:
            self._imagePaths["thumb"] = self._imageGlobal % image

    def set_date(self, date, date_format):
        """
        Sets Date Info Label

        date : string --- Date of list item
        date_format : string --- Format of date string for strptime conversion

        >>> item = ListItem()
        >>> item.set_date("17/02/16", "%d/%m/%y")
        17.02.2016
        """
        converted_date = _strptime(date, date_format)
        self._infoLabels["date"] = _strftime("%d.%m.%Y", converted_date)  # 01.01.2009
        self._infoLabels["aired"] = _strftime("%Y-%m-%d", converted_date)  # 2009-01-01
        self._infoLabels["year"] = _strftime("%Y", converted_date)
        _sortAdd(xbmcplugin.SORT_METHOD_DATE)

    def set_duration(self, duration):
        """
        Sets duration Info

        Args:
            duration (str|unicode|int): string or unicode or integer

        Duration can be an integer or an integer represented as string or unicode.
        It can also be a hour:minute:second (52:45) value represented as a string or unicode
        that will be converted to a numeric value.

        >>> item = ListItem()
        >>> item.set_duration(3165)
        3165

        >>> item.set_duration(u"3165")
        3165

        >>> item.set_duration(u"52:45")
        3165
        """
        if isinstance(duration, basestring):
            if u":" in duration:
                # Split Time By Marker and Convert to Integer
                time_parts = duration.split(":")
                time_parts.reverse()
                duration = 0
                counter = 1

                # Multiply Each Time Delta Segment by it's Seconds Equivalent
                for part in time_parts:
                    duration += int(part) * counter
                    counter *= 60
            else:
                # Convert to Interger
                duration = int(duration)

        # Set Duration
        self._infoLabels["duration"] = duration
        _sortAdd(xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)

    def set_resume_point(self, start_point, total_time=None):
        """
        Set Resume Point for Kodi to start playing video

        Args:
            start_point (str|unicode): The starting point of the video as a numeric value
            total_time (str|unicode, optional): The total time of the video, if not given, total_time will be the
                                               duration set in the infoLabels
        """
        data = total_time or str(self._streamInfo["video"].get("duration")) or None
        self.setProperty("totaltime", data)
        self.setProperty("resumetime", start_point)

    def addStreamInfo(self, ishd=None, video_codec="h264", audio_codec="aac", audio_channels=2, language="en",
                      aspect=0):
        """
        Set Stream details like codec & resolutions

        Args:
            ishd (int, optional): Sets the HD/4K overlay flag, (default None)
                                  None = Unknown,
                                  0 = SD,
                                  1 = 720p,
                                  2 = 1080p,
                                  3 = 4k.
            video_codec (str, optional): Codec that was used for the video. (default h264)
            audio_codec (str, optional): Codec that was used for the audio. (default aac)
            audio_channels (int, optional): Number of audio channels. (default 2)
            language (str, optional): Language that the audio is in. (default en) (English)
            aspect (float, optional): The aspect ratio of the video as a float, (default 0)
                                      2.33 (21:9),
                                      1.78 (16:9),
                                      1.33 (4:3),
        """

        # Add audio details
        audio_info = self._streamInfo["audio"]
        audio_info["channels"] = audio_channels
        audio_info["language"] = language
        audio_info["codec"] = audio_codec

        # Add video details
        video_info = self._streamInfo["video"]
        video_info["codec"] = video_codec
        if aspect:
            video_info["aspect"] = aspect

        # Standard Definition
        if ishd == 0:
            video_info["width"] = 768
            video_info["height"] = 576

        # HD Ready
        elif ishd == 1:
            video_info["width"] = 1280
            video_info["height"] = 720
            video_info["aspect"] = 1.78

        # Full HD
        elif ishd == 2:
            video_info["width"] = 1920
            video_info["height"] = 1080
            video_info["aspect"] = 1.78

        # 4K
        elif ishd == 3:
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
            command = "XBMC.Container.Update(%s)" % cls.url_for_route(cls.route, query)
        else:
            command = "XBMC.Container.Update(%s?updatelisting=true)" % cls.url_for_route(cls.route)

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
            command = "XBMC.Container.Update(%s)" % cls.url_for_route(cls.route, query)
        else:
            command = "XBMC.Container.Update(%s?updatelisting=true)" % cls.url_for_route(cls.route)

        # Append Command to context menu
        self._contextMenu.append((label, command))

    def __setitem__(self, key, value):
        self._urlQuerys[key] = value

    def update(self, _dict):
        self._urlQuerys.update(_dict)

    def __contains__(self, key):
        return key in self._urlQuerys

    def _get(self, path, list_type, is_folder, isplayable):
        """
        Returns a tuple of listitem properties, (path, listitem, is_folder)

        Args:
            path (str): url of video or addon to send to kodi
            list_type (str): Type of listitem content that will be send to kodi. Option are (video:audio)
            is_folder (bool): True if listing folder items else False for video items
            isplayable (bool): Whether the listitem is playable or not

        Returns:
            tuple:
        """

        # Set Kodi InfoLabels
        self.setInfo(list_type, self._infoLabels)

        # Set streamInfo if found
        if self._streamInfo["video"]:
            _listItem.addStreamInfo(self, "video", self._streamInfo["video"])
        if self._streamInfo["audio"]:
            _listItem.addStreamInfo(self, "audio", self._streamInfo["audio"])

        if is_folder:
            # Change Kodi Propertys to mark as Folder
            self.setProperty("isplayable", "false")
            self.setProperty("folder", "true")

            # Set Kodi icon image if not already set
            if "icon" not in self._imagePaths:
                self._imagePaths["icon"] = "DefaultFolder.png"

        else:
            # Change Kodi Propertys to mark as Folder
            self.setProperty("isplayable", "true" if isplayable else "false")
            self.setProperty("folder", "false")

            # Set Kodi icon image if not already set
            if "icon" not in self._imagePaths:
                self._imagePaths["icon"] = "DefaultVideo.png"

            # Add Video Specific Context menu items
            self._contextMenu.append(("$LOCALIZE[13347]", "XBMC.Action(Queue)"))
            self._contextMenu.append(("$LOCALIZE[13350]", "XBMC.ActivateWindow(videoplaylist)"))

            # Increment vid counter for later guessing of content list_type
            VirtualFS.vidCounter += 1

        # Add Context menu items
        self.addContextMenuItems(self._contextMenu)

        # Set listitem art
        _listItem.setArt(self, self._imagePaths)

        # Return Tuple of url, listitem, is_folder
        return path, self, is_folder

    def get(self, cls, list_type="video"):
        """
        Takes a class to route to and returns a tuple of listitem properties, (path, listitem, isFolder)

        Args:
            cls (obj): Class that will be called by the related video context menu item
            list_type (str, optional): Type of listitem content that will be send to kodi. Option are (video:audio)
                                       (default video)
        """

        # Create path to send to Kodi
        path = cls.url_for_route(cls.route, self._urlQuerys)

        # Return Tuple of url, listitem, isFolder
        return self._get(path, list_type, cls.isFolder, cls.isplayable)

    def get_route(self, route_path, list_type="video"):
        """
        Takes a route_path to a class and Returns a tuple of listitem properties, (path, listitem, isFolder)

        Args:
            route_path (str): Route that will be called by the related video context menu item
            list_type (str, optional): Type of listitem content that will be send to kodi. Option are (video:audio)
                                       (default video)
        """
        cls = cls_for_route(route_path, raise_on_error=True)
        return self.get(cls, list_type)

    def get_direct(self, path, list_type="video"):
        """
        Take a direct url for kodi to use and Returns a tuple of listitem properties, (path, listitem, isFolder)

        path : string ---
        [list_type] : string ---

        Args:
            path (str): url of video or addon to send to kodi
            list_type (str, optional): Type of listitem content that will be send to kodi. Option are (video:audio)
                                       (default video)
        """

        # Return Tuple of url, listitem, isFolder
        return self._get(path, list_type, False, True)

    @classmethod
    def add_item(cls, action_cls, label, url=None, thumbnail=None):
        """
        Basic constructor to add a simple listitem

        action_cls : class --- Class that will be call to show recent results
        label : string or unicode --- Lable of Listitem
        [url] : dict --- Url params to pass to listitem
        [thumbnail] : string or unicode --- Thumbnail image of listitem
        """
        listitem = cls()
        listitem.setLabel(label)
        if thumbnail:
            listitem.set_thumb(thumbnail)
        if url:
            listitem.update(url)
        return listitem.get(action_cls)

    @classmethod
    def add_next(cls, url=None):
        """
        A Listitem constructor for Next Page Item

        url: dict --- Dictionary containing url querys to control addon
        """

        # Fetch current url query
        base_url = Base.copy()
        if url:
            base_url.update(url)
        base_url["updatelisting"] = "true"
        base_url["nextpagecount"] = int(base_url.get("nextpagecount", 1)) + 1

        # Create listitem instance
        listitem = cls()
        listitem.setLabel(u"[B]%s %i[/B]" % (Base.get_local_string("Next_Page"), base_url["nextpagecount"]))
        listitem.set_thumb(u"next.png", 2)
        listitem.update(base_url)

        # Fetch current route and return
        route_path = Base.urlObject.path.lower() if Base.urlObject.path else "/"
        return listitem.get_route(route_path)

    @classmethod
    def add_search(cls, action_cls, url, label=None):
        """
        A Listitem constructor to add Saved search Support to addon

        action_cls : class --- Class that will be farwarded to search dialog
        url : dict --- Dictionary containing url querys combine with search term
        label : string --- Lable of Listitem
        """
        listitem = cls()
        if label:
            listitem.setLabel("[B]%s[/B]" % label)
        else:
            listitem.setLabel("[B]%s[/B]" % Base.get_local_string("search"))
        listitem.set_thumb(u"search.png", 2)
        url["route"] = action_cls.route
        listitem.update(url)
        return listitem.get_route("/internal/SavedSearches")

    @classmethod
    def add_recent(cls, action_cls, url=None, label=None):
        """
        A Listitem constructor to add Recent Folder to addon

        action_cls : class --- Class that will be call to show recent results
        url : dict --- Dictionary containing url querys to pass to Most Recent Class
        label : string --- Lable of Listitem
        """
        listitem = cls()
        if url:
            listitem.update(url)
        if label:
            listitem.setLabel(u"[B]%s[/B]" % label)
        else:
            listitem.setLabel(u"[B]%s[/B]" % Base.get_local_string("Most_Recent"))
        listitem.set_thumb(u"recent.png", 2)
        return listitem.get(action_cls)

    @classmethod
    def add_youtube(cls, content_id, label=None, enable_playlists=True, wide_thumb=False):
        """
        A Listitem constructor to add a youtube channel to addon

        content_id : string --- ID of Youtube channel or playlist to list videos for
        label : string --- Title of listitem - default (-Youtube Channel)
        enable_playlists : boolean --- Set to True to enable listing of channel playlists, (defaults True)
        wide_thumb : boolean --- Set to True to use a wide thumbnail or False for normal thumbnail image (default False)
        """
        listitem = cls()
        if label:
            listitem.setLabel(u"[B]%s[/B]" % label)
        else:
            listitem.setLabel(u"[B]%s[/B]" % Base.get_local_string("Youtube_Channel"))
        if wide_thumb:
            listitem.set_thumb("youtubewide.png", 2)
        else:
            listitem.set_thumb("youtube.png", 2)
        listitem["contentid"] = content_id
        listitem["enable_playlists"] = str(enable_playlists).lower()
        return listitem.get_route("/internal/youtube/playlist")


class Executer(Base):
    _isFolder = False
    _isplayable = False


class VirtualFS(Base):
    isFolder = True
    isplayable = False
    __listitem = None
    vidCounter = 0

    @abc.abstractmethod
    def start(self):
        """
        Abstractmethod thats required to be overridden by subclassing
        and is the starting point for the addon to load
        """
        pass

    @staticmethod
    def finalize():
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
        super(VirtualFS, self).__init__()
        listitems = self.start()
        self._send_to_kodi(listitems)

        # Call Finalize Method if Exists
        try:
            self.finalize()
        except Exception as e:
            logger.error("Failed to execute finalized function")
            logger.error(e)

    @property
    def listitem(self):
        """ Return a custom kodi listitem object """
        if self.__listitem is not None:
            return self.__listitem
        else:
            ListItem._fanart = self.fanart
            ListItem._strRelated = self.get_local_string("Related_Videos")
            ListItem._imageLocal = os.path.join(self.path, u"resources", u"media", u"%s")
            ListItem._imageGlobal = os.path.join(self._path_global, u"resources", u"media", u"%s")
            ListItem._refreshContext = (
                "$LOCALIZE[184]", "XBMC.Container.Update(%s)" % self.url_for_current({"refresh": "true"}))
            self.__listitem = ListItem
            return ListItem

    def _send_to_kodi(self, listitems):
        """ Add Directory List Items to Kodi """
        if listitems:
            # Convert results from generator to list
            listitems = list(listitems)

            # Add listitems to
            xbmcplugin.addDirectoryItems(self.handle, listitems, len(listitems))

            # Set Kodi Sort Methods
            _handle = self.handle
            _addSortMethod = xbmcplugin.addSortMethod
            for sortMethod in sorted(_sortMethods):
                _addSortMethod(_handle, sortMethod)

            # Guess Content Type and set View Mode
            is_folder = self.vidCounter < (len(listitems) / 2)
            # xbmcplugin.setContent(handle, "files" if isFolder else "episodes")
            self._set_view_mode("folder" if is_folder else "video")

        # End Directory Listings
        update_listing = u"updatelisting" in self and self[u"updatelisting"] == u"true"
        cache_to_disc = "cachetodisc" in self
        xbmcplugin.endOfDirectory(self.handle, bool(listitems), update_listing, cache_to_disc)

    def _set_view_mode(self, mode):
        """ Returns selected View Mode setting if available """
        setting_key = "%s.%s.view" % (xbmc.getSkinDir(), mode)
        view_mode = self.get_setting(setting_key, True)
        if view_mode:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_mode.encode("utf8"))


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

    @staticmethod
    def finalize():
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
        super(PlayMedia, self).__init__()
        self.__headers = []
        self.__mimeType = self.get("mimetype")

        # Resolve Video Url
        resolved = self.resolve()
        self._send_to_kodi(resolved)

        # Call Finalize Method if Exists
        try:
            self.finalize()
        except Exception as e:
            logger.error("Failed to execute finalize method")
            logger.error("Reason: %s", e)

    def set_mime_type(self, value):
        """ Set the mimeType of the video """
        if isinstance(value, unicode):
            value = value.encode("ascii")
        self.__mimeType = value

    def set_user_agent(self, useragent):
        """ Add a User Agent header to kodi request """
        if isinstance(useragent, unicode):
            useragent = useragent.encode("ascii")
        self.__headers.append("User-Agent=%s" % urllib.quote_plus(useragent))

    def set_referer(self, referer):
        """ Add a Referer header to kodi request """
        if isinstance(referer, unicode):
            referer = referer.encode("ascii")
        self.__headers.append("Referer=%s" % urllib.quote_plus(referer))

    def create_playlist(self, urls):
        """
        Create playlist for kodi and returns back the first item of that playlist to play

        url : iterable --- set of urls that will be used in the creation of the playlist
        """

        # Create Playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        first_item = None

        # Loop each item to create playlist
        for count, url in enumerate(urls, 1):
            # Create Listitem
            listitem = _listItem()
            listitem.setLabel(u"%s Part %i" % (self[u"title"], count))
            if self.__mimeType:
                listitem.setMimeType(self.__mimeType)
            url = self._check_url(url)
            listitem.setPath(url)

            # Populate Playlis
            playlist.add(url, listitem)
            if first_item is None:
                first_item = listitem

        # Return first playlist item to send to kodi
        return first_item

    def creat_loopback(self, url, **extra_params):
        """
        Create a playlist where the second item loops back to current addon to load next video
        e.g. Party Mode

        url : string or unicode --- url for the first listitem in the playlist to use
        extra_params : kwargs --- extra params to add to the loopback request to access the next video
        """

        # Create Playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

        # Create Main listitem
        main_item = _listItem()
        main_item.setLabel(self[u"title"])
        if self.__mimeType:
            main_item.setMimeType(self.__mimeType)
        url = self._check_url(url)
        main_item.setPath(url)
        playlist.add(url, main_item)

        # Create Loopback listitem
        loop_item = _listItem()
        loop_item.setLabel("Loopback")
        url = self.url_for_current(extra_params)
        loop_item.setPath(url)
        playlist.add(url, loop_item)

        # Return main listitem
        return main_item

    def extract_source(self, url, quality=None):
        """
        Extract video url using Youtube-DL

        url : string or unicode --- Url to fetch video for
        [quality] : integer --- Quality value to pass to StreamExtractor (default None)

        quality is 0=SD, 1=720p, 2=1080p, 3=4K
        """
        import YDStreamExtractor
        video_info = YDStreamExtractor.getVideoInfo(url, quality)

        # If there is more than one stream found then ask for selection
        if video_info.hasMultipleStreams():
            return self.source_selection(video_info)
        else:
            return video_info.streamURL()

    def source_selection(self, video_info):
        """ Ask user with video stream to play """
        display_list = []
        for stream in video_info.streams():
            data = "%s - %s" % (stream["ytdl_format"]["extractor"].title(), stream["title"])
            display_list.append(data)

        dialog = xbmcgui.Dialog()
        ret = dialog.select(self.get_local_string("Select_playback_item"), display_list)
        if ret >= 0:
            video_info.selectStream(ret)
            return video_info.streamURL()
        else:
            return None

    def _check_url(self, url):
        """ Check if there are any headers to add to url and return url and a string """
        if isinstance(url, unicode):
            url = url.encode("ascii")
        if self.__headers:
            url = "%s|%s" % (url, "&".join(self.__headers))
        return url

    def _send_to_kodi(self, resolved):
        """ Construct playable listitem and send to kodi """

        # Use resoleved as is if its already a listitem
        if isinstance(resolved, _listItem):
            listitem = resolved

        # Create listitem object if resolved object is a basestring (string/unicode)
        elif isinstance(resolved, basestring):
            listitem = _listItem()
            if self.__mimeType:
                listitem.setMimeType(self.__mimeType)
            resolved = self._check_url(resolved)
            listitem.setPath(resolved)

        # No valid resolved value was found
        else:
            raise ValueError("Url resolver returned invalid Url: %r" % resolved)

        # Send playable listitem to kodi
        xbmcplugin.setResolvedUrl(self.handle, True, listitem)

    @staticmethod
    def youtube_video_url(videoid):
        """
        Return url that redirects to youtube addon to play video

        videoid : string --- ID of the video to play
        """
        return u"plugin://plugin.video.youtube/play/?video_id=%s" % videoid

    @staticmethod
    def youtube_playlist_url(playlistid, mode=u"normal"):
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


@route("/internal/setViewMode")
class ViewModeSelecter(Base):
    """
    Class for displaying list of available skin view modes.
    Allowing for the selection of a view mode that will be force when
    displaying listitem content. Works with both video & folder views separately

    NOTE
    Must be called as a script only
    """

    def __init__(self):
        # Instance variables
        super(ViewModeSelecter, self).__init__()
        self.skinID = xbmc.getSkinDir()
        self.mode = self[u"arg1"]

        # Fetch databse of skin codes
        skincode_path = os.path.join(self._path_global, u"resources", u"data", u"skincodes.json")
        try:
            database = self.dict_storage(skincode_path)
        except (IOError, OSError) as e:
            self.debug("Was unable to load skincodes databse: %s", repr(e))
            skin_codes = {}
        else:
            # Fetch codes for current skin and mode
            if self.skinID in database:
                skin_codes = self.filter_codes(database)
            else:
                self.debug("No skin codes found for skin: %s", self.skinID)
                skin_codes = {}

        # Display list of view modes available
        new_mode = self.display(skin_codes)

        # Save new mode to setting
        if new_mode is not None:
            self.set_setting("%s.%s.view" % (self.skinID, self.mode), new_mode)

    def filter_codes(self, database):
        """ Filter codes down to current sky and mode """
        filterd = {}
        for mode, views in database[self.skinID].iteritems():
            if mode == self.mode or mode == u"both":
                for view in views:
                    key = self.get_local_string(view[u"id"]) if view[u"id"] is not None else u""
                    if u"combine" in view:
                        key = u"%s %s" % (key, view[u"combine"])
                    filterd[key.strip()] = view[u"mode"]

        return filterd

    def display(self, skin_codes):
        """ Display list of viewmodes that are available and return user selection """

        # Fetch currently saved setting if it exists
        try:
            current_mode = self.get_setting("%s.%s.view" % (self.skinID, self.mode))
        except ValueError:
            current_mode = ""

        # Create list of item to show to user
        reference = [None]
        show_list = [self.get_local_string("Default")]
        for name, mode in skin_codes.iteritems():
            reference.append(mode)
            if current_mode and current_mode == mode:
                show_list.append(u"[B]-%s[/B]" % name)
            else:
                show_list.append(name)

        # Append custom option to showlist including current mode if its custom
        if current_mode and current_mode not in skin_codes.values():
            custom = u"[B]-%s (%i)[/B]" % (self.get_local_string("Custom"), current_mode)
        else:
            custom = self.get_local_string("Custom")
        show_list.append(custom)

        # Display List to User
        dialog = xbmcgui.Dialog()
        ret = dialog.select(self.utils.get_skin_name(self.skinID), show_list)
        if ret == 0:
            self.debug("Reseting viewmode setting to default")
            return ""
        elif ret == len(show_list) - 1:
            new_mode = self.ask_for_view_id(current_mode)
            if new_mode:
                self.debug("Saving new custom viewmode setting: %s", new_mode)
            return new_mode
        elif ret > 0:
            new_mode = str(reference[ret])
            self.debug("Saving new viewmode setting: %s", new_mode)
            return new_mode

    def ask_for_view_id(self, current_mode):
        """ Ask the user what custom view mode to use """
        dialog = xbmcgui.Dialog()
        ret = dialog.numeric(0, self.get_local_string("Enter_number"), str(current_mode))
        if ret:
            return str(ret)
        else:
            return None


@route("/internal/SavedSearches")
class SavedSearches(VirtualFS):
    """
    Class used to list all saved searches for the addon that called it.
    Usefull to add search support to addon that will also keep track of previous searches
    Also contains option via context menu to remove old search terms.
    """
    searches = None

    def start(self):
        # Fetch list of current saved searches
        self.searches = searches = self.set_storage(u"searchterms.json")

        # Remove term from saved searches if remove argument was passed
        if self.get("remove") in searches:
            searches.remove(self.pop("remove"))
            searches.sync()

        # Show search dialog if search argument was passed or there is not search term saved
        elif not searches or self.pop("search", None) is not None:
            self.search_dialog()

        # List all saved search terms
        try:
            return self.list_terms()
        finally:
            searches.close()

    def search_dialog(self):
        """ Show dialog for user to enter a new search term """
        ret = self.utils.Keyboard("", self.get_local_string("Enter_search_string"), False)
        if ret:
            # Add searchTerm to database
            self.searches.add(ret)
            self.searches.sync()

    def list_terms(self):
        """ List all saved search terms """

        # Create Speed vars
        base_url = self["url"]
        listitem = self.listitem
        farwarding_route = self[u"route"]

        # Add search listitem entry
        item = listitem()
        item.setLabel(u"[B]%s[/B]" % self.get_local_string("search"))
        query = self.copy()
        query["search"] = "true"
        query["updatelisting"] = "true"
        query["cachetodisc"] = "true"
        item.update(query)
        yield item.get(self)

        # Create Context Menu item Params
        str_remove = self.get_local_string("Remove")
        query_cx = self.copy()
        query_li = self.copy()

        # Loop earch search item
        for searchTerm in self.searches:
            # Create listitem of Data
            item = listitem()
            item.setLabel(searchTerm.title())
            query_li["url"] = base_url % searchTerm
            item.update(query_li)

            # Creatre Context Menu item to remove search item
            query_cx["remove"] = searchTerm
            item.menu_update(self, str_remove, **query_cx)

            # Return Listitem data
            yield item.get_route(farwarding_route)
