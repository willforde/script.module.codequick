# Standard Library Imports
import urllib
import os

# Fetch date convertion tools
from time import strptime, strftime

# Kodi Imports
import xbmcplugin
import xbmcgui
import xbmc

# Package imports
from .support import strings, logger, handle, params, get_info, get_setting, localize, current_path
from .support import _route_store, selected_route, get_addon_data, RouteData

# Setup sort method set
sortMethods = {xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE}
sortAdd = sortMethods.add
sort_map = {"size": (xbmcplugin.SORT_METHOD_SIZE, long),
            "date": (xbmcplugin.SORT_METHOD_DATE, None),
            "genre": (xbmcplugin.SORT_METHOD_GENRE, None),
            "studio": (xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE, None),
            "count": (xbmcplugin.SORT_METHOD_PROGRAM_COUNT, int),
            "rating": (xbmcplugin.SORT_METHOD_VIDEO_RATING, float),
            "episode": (xbmcplugin.SORT_METHOD_EPISODE, int)}

# Update string references
strings.update(search=137,
               next_page=33078,
               most_recent=32902,
               related_videos=32903,
               youtube_channel=32901,
               select_playback_item=25006)


def execute(route_path):
    """
    This is the route decorator that is used when executing code as a script.

    Parameters
    ----------
    route_path : bytestring
        The route path that will be used to map to the decorated function.

    Returns
    -------
    :class:`Executer`
        A class that handles the routed function.
    """
    return Executer.register(route_path)


def route(route_path):
    """
    This is the main route decorator that is used for listing of listitems, video or folders.

    Parameters
    ----------
    route_path : bytestring
        The route path that will be used to map to the decorated function.

    Returns
    -------
    :class:`VirtualFS`
        A class that handles the routed function.
    """
    return VirtualFS.register(route_path)


def resolve(route_path):
    """
    This is the route decorator that is used when resolving a video url from a site.

    Parameters
    ----------
    route_path : bytestring
        The route path that will be used to map to the decorated function.

    Returns
    -------
    :class:`PlayMedia`
        A class that handles the routed function.
    """
    return PlayMedia.register(route_path)


class Executer(RouteData):
    is_playable = False
    is_folder = False

    def execute(self):
        """Execute the function"""
        self._func()


class VirtualFS(RouteData):
    is_playable = False
    is_folder = True

    def execute(self):
        """Add Directory List Items to Kodi"""

        # Fetch the list of listitems
        listitems = self._func()

        if listitems is None:
            self.__end_directory(False)
        else:
            listitems = list(listitems)
            if listitems:
                # Add listitems to kodi
                xbmcplugin.addDirectoryItems(handle, listitems, len(listitems))

                # Set Kodi Sort Methods
                _addSortMethod = xbmcplugin.addSortMethod
                for sortMethod in sorted(sortMethods):
                    _addSortMethod(handle, sortMethod)

                # Guess Content Type and View Mode
                is_folder = ListItem.vidCounter < (len(listitems) / 2)
                self.__content_type(is_folder)

                self.__end_directory(True)
            else:
                self.__end_directory(False)
                raise RuntimeError("No listitems ware loaded")

    @staticmethod
    def __content_type(isfolder):
        """Guess content type and set kodi parameters, setContent & SetViewMode """
        xbmcplugin.setContent(handle, "files" if isfolder else "episodes")
        listing_type = "folder" if isfolder else "video"
        set_key = "%s.%s.view" % (xbmc.getSkinDir(), listing_type)
        view_mode = get_setting(set_key, raw_setting=True)
        if view_mode:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % str(view_mode))

    @staticmethod
    def __end_directory(success):
        """Mark the end of directory listings"""
        cache_to_disc = u"cachetodisc" in params
        update_listing = u"refresh" in params or (u"updatelisting" in params and params[u"updatelisting"] == u"true")
        xbmcplugin.endOfDirectory(handle, success, update_listing, cache_to_disc)


class PlayMedia(RouteData):
    is_playable = True
    is_folder = False

    def __init__(self, *args, **kwargs):
        super(PlayMedia, self).__init__(*args, **kwargs)

        # Monkey patch in the youtube url builder functions
        from .youtube import build_video_url, build_playist_url
        setattr(self, "youtube_playlist_url", build_playist_url)
        setattr(self, "youtube_video_url", build_video_url)

        # Instance Vars
        self.__headers = []
        self.__mimetype = None

    def execute(self):
        """Resolve Video Url"""
        try:
            resolved = self._func(self)
        except TypeError as e:
            if "takes no arguments" in str(e):
                raise TypeError("Resolver function must accept tools argument")
            else:
                raise
        else:
            assert resolved, "Unable to resolve url"
            self.__send_to_kodi(resolved)

    def set_mime_type(self, value):
        """
        Set the mimeType of the video.

        Parameters
        ----------
        value : bytestring
            The mimetype of the video.
        """
        self.__mimetype = str(value)

    def set_user_agent(self, useragent):
        """
        Add a User Agent header to kodi request.

        Parameters
        ----------
        useragent : bytestring
            The user agent for kodi to use.
        """
        useragent = "User-Agent=%s" % urllib.quote_plus(str(useragent))
        self.__headers.append(useragent)

    def set_referer(self, referer):
        """
        Add a Referer header to kodi request

        Parameters
        ----------
        referer : bytestring
            The referer for kodi to use.
        """
        referer = "Referer=%s" % urllib.quote_plus(str(referer))
        self.__headers.append(referer)

    def create_playlist(self, urls, shuffle=False):
        """
        Create playlist for kodi and returns back the first item of that playlist to play

        Parameters
        ----------
        urls : list
            Set of urls that will be used in the creation of the playlist.

        shuffle : bool, optional(default=False)
            If set to True then the playlist will be shuffled

        Returns
        -------
        :class:`xbmcgui.ListItem`
            The first listitem of the playlist
        """

        # Create Playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

        # Loop each item to create playlist
        for count, url in enumerate(urls, 1):
            listitem = xbmcgui.ListItem()
            listitem.setLabel(u"%s Part %i" % (params[u"title"], count))
            url = self.__check_url(url)
            listitem.setPath(url)

            # Set mimetype if any
            if self.__mimetype:
                listitem.setMimeType(self.__mimetype)

            # Populate Playlis
            playlist.add(url, listitem)

        # Shuffle playlist if required
        if shuffle is True:
            playlist.shuffle()

        # Return first playlist item to send to kodi
        return playlist[0]

    def creat_loopback(self, url, **next_params):
        """
        Create a playlist where the second item loops back to current addon to load next video. e.g. Party Mode

        Parameters
        ----------
        url : unicode
            Url for the first playable listitem to use.

        next_params : kwargs, optional
            Extra params to add to the loopback request to access the next video.

        Returns
        -------
        :class:`xbmcgui.ListItem`
            The Listitem that kodi will play
        """

        # Create Playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

        # Create Main listitem
        main_listitem = xbmcgui.ListItem()
        main_listitem.setLabel(params[u"title"])
        if self.__mimetype:
            main_listitem.setMimeType(self.__mimetype)

        url = self.__check_url(url)
        main_listitem.setPath(url)
        playlist.add(url, main_listitem)

        # Create Loopback listitem
        loop_listitem = xbmcgui.ListItem()
        loop_listitem.setLabel("Loopback")
        loopback_url = current_path(**next_params)
        loop_listitem.setPath(loopback_url)
        playlist.add(loopback_url, loop_listitem)

        # Return main listitem
        return main_listitem

    def extract_source(self, url, quality=None):
        """
        Extract video url using YoutubeDL

        Parameters
        ----------
        url : str
            Url to fetch video for.

        quality : int, optional(default=None)
            Quality value to pass to StreamExtractor.

            0=SD
            1=720p
            2=1080p
            3=4K

        Returns
        -------
        str:
            The extracted video url
        """
        # Sence youtubeDL is optional, return None when youtubeDL is not found
        try:
            import YDStreamExtractor
        except ImportError:
            logger.debug("YoutubeDL module not installed. Please install to enable 'extract_source'")
            return None

        # If there is more than one stream found then ask for selection
        video_info = YDStreamExtractor.getVideoInfo(url, quality)
        if video_info.hasMultipleStreams():
            return self.__source_selection(video_info)
        else:
            return video_info.streamURL()

    def __check_url(self, url):
        """
        Check if there are any headers to add to url and return url as a string

        Parameters
        ----------
        url : unicode
            Url to add headers to.

        Returns
        -------
        str
            Url with the headers added
        """
        if self.__headers:
            url = "%s|%s" % (str(url), "&".join(self.__headers))
        return url

    def __send_to_kodi(self, resolved):
        """ Construct playable listitem and send to kodi

        Parameters
        ----------
        resolved : bytestring, :class:`xbmcgui.ListItem`
            The resolved url to send back to kodi

        Raises
        -------
        ValueError
            Will be raised if the resolved url is not of type listitem or bytestring
        """

        # Use resoleved as is if its already a listitem
        if isinstance(resolved, xbmcgui.ListItem):
            listitem = resolved

        # Create listitem object if resolved object is a basestring (string/unicode)
        elif isinstance(resolved, basestring):
            listitem = xbmcgui.ListItem()
            if self.__mimetype:
                listitem.setMimeType(self.__mimetype)

            resolved = self.__check_url(resolved)
            listitem.setPath(resolved)

        # No valid resolved value was found
        else:
            raise ValueError("Url resolver returned invalid Url: %r" % resolved)

        # Send playable listitem to kodi
        xbmcplugin.setResolvedUrl(handle, True, listitem)

    @staticmethod
    def __source_selection(video_info):
        """
        Ask user with video stream to play

        Parameters
        ----------
        video_info : dict
            YDStreamExtractor video_info dict

        Returns
        -------
        str, optional
            Stream url of video
        """
        display_list = []
        for stream in video_info.streams():
            data = "%s - %s" % (stream["ytdl_format"]["extractor"].title(), stream["title"])
            display_list.append(data)

        dialog = xbmcgui.Dialog()
        ret = dialog.select(localize("select_playback_item"), display_list)
        if ret >= 0:
            video_info.selectStream(ret)
            return video_info.streamURL()
        else:
            return None


class Art(dict):
    _image_local = os.path.join(get_info("path"), u"resources", u"media", u"%s")
    _image_global = os.path.join(get_info("path_global"), u"resources", u"media", u"%s")
    _fanart = get_info("fanart")

    def __init__(self):
        super(Art, self).__init__()
        if self._fanart:
            self["fanart"] = self._fanart

    def local_thumb(self, image):
        # noinspection PyTypeChecker
        self["thumb"] = self._image_local % image

    def global_thumb(self, image):
        # noinspection PyTypeChecker
        self["thumb"] = self._image_global % image


class Info(dict):
    def __setitem__(self, key, value):
        # Convert duration into an integer if required
        if value is None:
            logger.debug("None type value detected for info label %s, Ignoring", key)
        elif key == "duration":
            value = self._duration(value)
            sortAdd(xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
        else:
            try:
                sort_type, type_converter = sort_map[key]
            except KeyError:
                pass
            else:
                sortAdd(sort_type)
                if type_converter:
                    try:
                        value = type_converter(value)
                    except ValueError:
                        raise ValueError("Value for %s, %s is not of %s" % (key, value, type_converter))

        # Set the updated value
        super(Info, self).__setitem__(key, value)

    def date(self, date, date_format):
        converted_date = strptime(date, date_format)
        self["date"] = strftime("%d.%m.%Y", converted_date)  # 01.01.2009
        self["aired"] = strftime("%Y-%m-%d", converted_date)  # 2009-01-01
        self["year"] = int(strftime("%Y", converted_date))  # 2009

    @staticmethod
    def _duration(duration):
        if isinstance(duration, basestring):
            if u":" in duration:
                # Split Time By Marker and Convert to Integer
                time_parts = duration.split(u":")
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

        return duration


class Stream(object):
    def __init__(self):
        self.video = {}
        self.audio = {"channels": 2}
        self.subtitle = {}

    def add(self, stream_type, values):
        """
        Add a stream with details.

        Parameters
        ----------
        stream_type : str
            Type of stream(video/audio/subtitle).

        values : dict
            pairs of { label: value }.
        """
        if stream_type == "video":
            self.video.update(values)
        elif stream_type == "audio":
            self.audio.update(values)
        elif stream_type == "subtitle":
            self.subtitle.update(values)

    def hd(self, value, aspect=None):
        """
        Set the required stream info to show HD/4K logos.

        Parameters
        ----------
        value : int
            0 = SD
            1 = 720p
            2 = 1080p
            3 = 4K

        aspect : float, optional
            The aspect of the video
        """
        video_info = self.video

        # Skip if value is None, Unknown
        if value is None:
            return None

        # Standard Definition
        elif value == 0:
            video_info["width"] = 768
            video_info["height"] = 576

        # HD Ready
        elif value == 1:
            video_info["width"] = 1280
            video_info["height"] = 720
            if not aspect:
                aspect = 1.78

        # Full HD
        elif value == 2:
            video_info["width"] = 1920
            video_info["height"] = 1080
            if not aspect:
                aspect = 1.78

        # 4K
        elif value == 3:
            video_info["width"] = 3840
            video_info["height"] = 2160
            if not aspect:
                aspect = 1.78

        # Set aspect if not already set, won't override
        if aspect and "aspect" not in video_info:
            video_info["aspect"] = aspect


class Context(list):
    _strRelated = localize("related_videos")
    _refreshContext = ("$LOCALIZE[184]", "XBMC.Container.Update(%s)" % current_path(refresh="true"))

    def __init__(self):
        super(Context, self).__init__()
        self.append(self._refreshContext)

    def related(self, func, **query):
        self.add(func, self._strRelated, **query)

    def add(self, func, label, **query):
        if query:
            if "updatelisting" not in query:
                query["updatelisting"] = "true"
            command = "XBMC.Container.Update(%s)" % func.kodi_path(query)
        else:
            command = "XBMC.Container.Update(%s?updatelisting=true)" % func.kodi_path()

        # Append Command to context menu
        self.append((label, command))


class ListItem(object):
    vidCounter = 0

    def __init__(self):
        self.art = Art()
        self.url = dict()
        self.info = Info()
        self.stream = Stream()
        self.property = dict()
        self.context = Context()
        self.listitem = xbmcgui.ListItem()
        self.label = None

    def set_mimetype(self, value):
        """ Sets the listitem's mimetype if known. """
        self.listitem.setMimeType(value)

    def disable_content_lookup(self):
        """ Disable content lookup for item. """
        self.listitem.setContentLookup(False)

    def get(self, path, list_type="video"):
        """
        Take a url that can be directly sent to kodi and then returns a tuple of (path, listitem, isfolder)

        Parameters
        ----------
        path : basestring or route
            Url of video or addon to send to kodi.

        list_type : str, optional(default='video')
            Type of listitem content that will be send to kodi. Option are (video:audio).

        Returns
        -------
        str
            Path to send to kodi.

        :class:`xbmcgui.ListItem`
            Listitem to send to kodi.

        bool
            Whether the listitem is a folder or not.
        """

        if isinstance(path, RouteData):
            folder = path.is_folder
            playable = path.is_playable
            path = path.kodi_path(self.url)
        else:
            folder = False
            playable = True

        label = self.label
        assert label, "No label set on listitem"
        listitem = self.listitem
        listitem.setLabel(label)
        self.info["title"] = label

        # Set Kodi InfoLabels
        listitem.setInfo(list_type, self.info)

        # Set streamInfo if found
        if self.stream.audio:
            listitem.addStreamInfo("audio", self.stream.audio)
        if self.stream.video:
            listitem.addStreamInfo("video", self.stream.video)
        if self.stream.subtitle:
            listitem.addStreamInfo("subtitle", self.stream.subtitle)

        # Set listitem propertys
        for key, value in self.property:
            listitem.setProperty(key, value)

        if folder:
            # Change Kodi Propertys to mark as Folder
            listitem.setProperty("isplayable", "false")
            listitem.setProperty("folder", "true")

            # Set Kodi icon image if not already set
            if "icon" not in self.art:
                self.art["icon"] = "DefaultFolder.png"
        else:
            # Change Kodi Propertys to mark as Folder
            listitem.setProperty("isplayable", "true" if playable else "false")
            listitem.setProperty("folder", "false")

            # Set Kodi icon image if not already set
            if "icon" not in self.art:
                self.art["icon"] = "DefaultVideo.png"

            # Add Video Specific Context menu items
            self.context.append(("$LOCALIZE[13347]", "XBMC.Action(Queue)"))
            self.context.append(("$LOCALIZE[13350]", "XBMC.ActivateWindow(videoplaylist)"))

            # Add the title to the url dict for later use by the url resolver
            self.url["title"] = label.encode("ascii", "ignore")

            # Increment vid counter for later guessing of content list_type
            ListItem.vidCounter += 1

        # Add Context menu items
        listitem.addContextMenuItems(self.context)

        # Set listitem art
        listitem.setArt(self.art)

        # Return Tuple of url, listitem, isfolder
        return path, listitem, folder

    @classmethod
    def add_dict(cls, data):
        listitem = cls()
        listitem.label = data["label"]

        if "art" in data:
            listitem.art.update(data["art"])
        if "info" in data:
            listitem.info.update(data["info"])
        if "url" in data:
            listitem.url.update(data["url"])
        if "property" in data:
            listitem.property.update(data["property"])
        if "stream" in data:
            for stream_type, values in data["stream"].iteritems():
                listitem.stream.add(stream_type, values)

        return listitem.get(data["route"])

    @classmethod
    def add_item(cls, action, label, thumbnail=None, **url):
        """
        Basic constructor to add a simple listitem.

        Parameters
        ----------
        action : object or str
            Class that will be call to show recent results

        label : basestring
            Label of Listitem

        thumbnail : bytestring, optional
            Thumbnail image of listitem

        url : dict, optional
            Url params to pass to listitem

        Returns
        -------
        tuple
            A tuple of path, listitem, isfolder
        """

        listitem = cls()
        listitem.label = label
        if thumbnail:
            listitem.art["thumb"] = thumbnail
        if url:
            listitem.url.update(url)

        return listitem.get(action)

    @classmethod
    def add_next(cls, **url):
        """
        A Listitem constructor for Next Page Item.

        Parameters
        ----------
        url : dict
            Dictionary containing url querys to control addon

        Returns
        -------
        tuple
            A tuple of path, listitem, isfolder
        """

        # Fetch current url query
        base_url = params.copy()
        base_url["updatelisting"] = "true"
        base_url["nextpagecount"] = str(int(base_url.get("nextpagecount", 1)) + 1)
        if url:
            base_url.update(url)

        # Create listitem instance
        listitem = cls()
        listitem.label = u"[B]%s %s[/B]" % (localize("next_page"), base_url["nextpagecount"])
        listitem.art.global_thumb(u"next.png")
        listitem.url.update(base_url)

        # Fetch current route and return
        return listitem.get(_route_store[selected_route])

    @classmethod
    def add_search(cls, action, label=None, **url):
        """
        A Listitem constructor to add Saved search Support to addon

        Parameters
        ----------
        action : func or unicode
            Class that will be farwarded to search dialog

        label : str, optional(default='search')
            Lable of Listitem

        url : dict
            Dictionary containing url querys to combine with search term

        Returns
        -------
        tuple
            A tuple of path, listitem, isfolder
        """

        listitem = cls()
        listitem.label = u"[B]%s[/B]" % (label if label else localize("search"))
        listitem.art.global_thumb(u"search.png")
        url["route"] = action.route
        listitem.url.update(url)

        return listitem.get(saved_searches)

    @classmethod
    def add_recent(cls, action, label=None, **url):
        """
        A Listitem constructor to add Recent Folder to addon.

        Parameters
        ----------
        action : :class:`Base`
            Class that will be call to show recent results.

        url : dict
            Dictionary containing url querys to pass to Most Recent Class.

        label : str, optional
            Lable of Listitem

        Returns
        -------
        tuple
            A tuple of path, listitem, isfolder
        """

        listitem = cls()
        listitem.label = u"[B]%s[/B]" % (label if label else localize("most_recent"))
        listitem.art.global_thumb(u"recent.png")
        if url:
            listitem.url.update(url)

        return listitem.get(action)

    @classmethod
    def add_youtube(cls, content_id, label=None, enable_playlists=True, wide_thumb=False):
        """
        A Listitem constructor to add a youtube channel to addon

        Parameters
        ----------
        content_id : unicode
            ID of Youtube channel or playlist to list videos for

        label : bytestring, optional
            Title of listitem - default to add_string_ref '-Youtube Channel'

        enable_playlists : bool, optional(default=True)
            Set to True to enable listing of channel playlists.

        wide_thumb : bool, optional(default=False)
            Set to True to use a wide thumbnail or False for normal thumbnail image.

        Returns
        -------
        tuple
            A tuple of path, listitem, isfolder
        """

        # Check if youtube addon exists before creating a listitem for it
        try:
            get_addon_data("plugin.video.youtube", "name")
        except RuntimeError:
            return False

        # Youtube exists, Creating listitem link
        listitem = cls()
        listitem.label = u"[B]%s[/B]" % (label if label else localize("youtube_channel"))
        listitem.art.global_thumb(u"youtubewide.png" if wide_thumb else u"youtube.png")
        listitem.url["contentid"] = content_id
        listitem.url["enable_playlists"] = str(enable_playlists).lower()
        return listitem.get("/internal/youtube/playlist")


@execute("/internal/setViewMode")
def view_mode_selecter():
    from .internal import ViewModeSelecter
    mode_selecter = ViewModeSelecter()
    new_mode = mode_selecter.display_modes()
    if new_mode is not None:
        mode_selecter.set_mode(new_mode)


@route("/internal/SavedSearches")
def saved_searches():
    from .internal import SavedSearches
    return SavedSearches().start()
