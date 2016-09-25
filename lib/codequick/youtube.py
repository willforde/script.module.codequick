# Standard Library Imports
import json
import os

# Package imports
from .support import strings, logger, params, get_info, localize, get_addon_setting, cleanup_functions, requests_session
from .storage import DictStorage, ShelfStorage
from .api import route, resolve, ListItem


# Prerequisites
strings.update(playlists=136, all_videos=16100)


@route(u"/internal/youtube/playlist", u"contentid")
def playlist(contentid):
    gdata = APIControl()
    return gdata.playlist(contentid)


@route(u"/internal/youtube/playlists", u"contentid")
def playlists(contentid):
    gdata = APIControl()
    return gdata.playlists(contentid, u"contentid" not in params)


@route(u"/internal/youtube/related", u"videoid")
def related(videoid):
    gdata = APIControl()
    return gdata.related(videoid)


def build_video_url(videoid):
    """
    Return url that redirects to youtube addon to play video

    Parameters
    ----------
    videoid : bytestring
        ID of the video to play.

    Returns
    -------
    unicode
        A plugin url to the youtube addon that will play the given video
    """
    return u"plugin://plugin.video.youtube/play/?video_id=%s" % videoid


def build_playist_url(playlistid, mode=u"normal"):
    """
    Return url that redirects to youtube addon to play playlist

    Parameters
    ----------
    playlistid : bytestring
        Id of the playlist to play.

    mode : bytestring, optional(default=u'normal')
        Order of the playlist.

        Available options are
        normal
        reverse
        shuffle

    Returns
    -------
    unicode
        A plugin url to the youtube addon that will play the given playlist
    """
    return u"plugin://plugin.video.youtube/play/?playlist_id=%s&mode=%s" % (playlistid, mode)


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
        return lang
    else:
        if setting:
            dash = setting.find(u"-")
            if dash > 0:
                return setting[:dash]

        return lang


class APIControl(object):
    """ Class to control the access to the youtube API """
    __video_data = __channel_data = __category_data = None

    def cleanup(self):
        """ Trim down the cache if cache gets too big """
        # Fetch video cache
        video_cache = self.__video_data
        if video_cache:
            # Check the amount of videos that are cached
            cache_len = len(video_cache)

            # Clean cache only when there is more than 2000 videos cached
            if cache_len > 2000:
                logger.debug("Running Youtube Cache Cleanup")
                remove_list = []
                dated = []

                # Filter out videos that are not public
                for vdata in video_cache.itervalues():
                    status = vdata[u"status"]
                    if status[u"privacyStatus"] == u"public" and status[u"uploadStatus"] == u"processed":
                        dated.append((vdata[u"snippet"][u"publishedAt"], vdata[u"id"], vdata[u"snippet"][u"channelId"]))
                    else:
                        remove_list.append(vdata[u"id"])

                # Sort cache by published date
                sorted_cache = sorted(dated)
                valid_channel_refs = set()

                # Remove 500 of the oldest videos
                for count, (published, videoid, channelid) in enumerate(sorted_cache):
                    if count < 500:
                        remove_list.append(videoid)
                    else:
                        # Sense cached item was not removed, mark the channelid as been referenced
                        valid_channel_refs.add(channelid)

                # If there are any video to remove then remove them and also remove any leftover channel references
                if remove_list:
                    # Remove all video that are marked for removel
                    for videoid in remove_list:
                        logger.debug("Removing cached video : %s", videoid)
                        del video_cache[videoid]

                    # Clean the channel cache of unreferenced channel ids
                    channel_cache = self._channel_data.get(u"channels")
                    if channel_cache:
                        sync = False
                        for channelid in channel_cache.keys():
                            if channelid not in valid_channel_refs:
                                del channel_cache[channelid]
                                sync = True

                        # Close connection to channel cache
                        channel_cache.close(sync)

            # Close connection to cache database
            video_cache.close()

    @property
    def _category_data(self):
        """ Return opened category_data database or connect to the category_data database and return """
        if self.__category_data is not None:
            return self.__category_data
        else:
            dir_path = os.path.join(get_info("profile_global"), u"youtube")
            self.__category_data = category_data = DictStorage(dir_path, u"category_data.json")
            return category_data

    @property
    def _channel_data(self):
        """ Return opened channel_data database or connect to the channel_data database and return """
        if self.__channel_data is not None:
            return self.__channel_data
        else:
            dir_path = os.path.join(get_info("profile"), u"youtube")
            self.__channel_data = channel_data = DictStorage(dir_path, u"channel_data.json")
            return channel_data

    @property
    def _video_data(self):
        """ Return opened video_data database or connect to the video_data database and return """
        if self.__video_data is not None:
            return self.__video_data
        else:
            dir_path = os.path.join(get_info("profile"), u"youtube")
            self.__video_data = video_data = ShelfStorage(dir_path, u"video_data.shelf")
            return video_data

    def _validate_uuid(self, contentid, playlist_uuid=True):
        """
        Check and return a valid content id for given type

        Note
        ----
        If playlist_type is true and if the content id was a channel name then the channel upload id will be
        returnd. If the playlist_type is false and the content id was a channel name then it will return the channel id.
        If the channel id was given then that id will be returnd if playlist_type is false else it will convert it
        to the upload id.

        Parameters
        ----------
        contentid : unicode
            ID of Youtube content to validate, Channel Name, Channel ID, Channel Uploads ID or Playlist ID

        playlist_uuid : bool, optional(default=True)
            True to return a playlistID/uploadID else False for a channelID

        Raises
        ------
        ValueError
            Will be raised if content id is a playlist id and playlist_type is false. Sense we can not match a
            playlist to a channel id.
        """

        # Quick Access Vars
        content_code = contentid[:2]
        channel_cache = self._channel_data
        channel_refs = channel_cache.setdefault(u"ref", {})
        channel_data = channel_cache.setdefault(u"channels", {})

        # Directly return the content id if its a playlistID or uploadsID and playlist_uuid is required
        if content_code == u"PL" or content_code == u"FL":
            if playlist_uuid:
                return contentid
            else:
                raise ValueError("Unable to link a playlist uuid to a channel uuid")

        # Return the channel uploads uuid if playlist_uuid is required else the channels uuid if we have a mapping for
        # said uploads uuid. Raises ValueError when unable to map the uploads uuid to a channel.
        elif content_code == u"UU":
            if playlist_uuid:
                return contentid
            elif contentid in channel_refs:
                return channel_refs[contentid]
            else:
                raise ValueError("Unable to link a channel uploads uuid to a channel uuid")

        # Check if content is a channel id
        elif content_code == u"UC":
            # Return the channel uuid as is
            if playlist_uuid is False:
                return contentid

            # Return the channels uploads uuid
            elif contentid in channel_data:
                return channel_data[contentid][u"uploads"]

            # Request channel data from server and return channels uploads uuid
            else:
                self._update_channel_cache(channel_id=contentid)
                return channel_data[contentid][u"uploads"]

        else:
            # Content id must be a channel name
            if contentid in channel_refs:
                channelid = channel_refs[contentid]
                if channelid not in channel_data:
                    self._update_channel_cache(channel_id=channelid)
            else:
                self._update_channel_cache(for_username=contentid)
                channelid = channel_refs[contentid]

            # Return the channel uploads uuid if playlist uuid is True else return the channel uuid
            if playlist_uuid:
                return channel_data[channelid][u"uploads"]
            else:
                return channelid

    def _update_channel_cache(self, channel_id=None, for_username=None):
        """
        Update on disk cache of channel information

        Parameters
        ----------
        channel_id : unicode or list of unicode, optional
            ID of the channel to request information for.

        for_username : unicode, optional
            Username of the channel to request information for.

        Note
        ----
        If both channel_id and for_username is given then channel_id will take priority.
        """
        # Make channels api request
        feed = self.api.channels(channel_id, for_username)

        # Fetch channel cache
        channel_cache = self._channel_data
        channel_refs = channel_cache.setdefault(u"ref", {})
        channel_data = channel_cache.setdefault(u"channels", {})

        # Update cache
        for item in feed[u"items"]:
            # Fetch common info
            title = item[u"snippet"][u"localized"][u"title"]
            description = item[u"snippet"][u"localized"][u"description"]
            uploads = item[u"contentDetails"][u"relatedPlaylists"][u"uploads"]

            # Fetch the channel banner if available
            if u"brandingSettings" in item:
                fanart = item[u"brandingSettings"][u"image"][u"bannerTvMediumImageUrl"]
            else:
                fanart = None

            # Set and save channel info into cache
            data = {"title": title, "description": description, "uploads": uploads, "fanart": fanart}
            channel_data[item[u"id"]] = data
            channel_refs[uploads] = item[u"id"]

        # Also add reference for channel name if given
        if for_username:
            channelid = feed[u"items"][0][u"id"]
            channel_refs[for_username] = channelid
            logger.debug("Channel ID for channel %s is %s", for_username, channelid)

        # Sync cache to disk
        channel_cache.sync()

    def _update_category_cache(self, cat_id=None):
        """
        Update on disk cache of category information

        Parameters
        ----------
        cat_id : unicode or list of unicode, optional(default=None)
            ID(s) of the categories to fetch category names for.

        Note
        ----
        If no category id is given then all categories names will be fetched.
        """

        # Fetch category Information
        feed = self.api.video_categories(cat_id)

        # Update category cache
        category_data = self._category_data
        for item in feed[u"items"]:
            category_data[item[u"id"]] = item[u"snippet"][u"title"]
        category_data.sync()

    def _update_video_cache(self, ids):
        """
        Update on disk cache of video information

        Parameters
        ----------
        ids : unicode or list of unicode
            ID(s) of videos to fetch information for.
        """

        # Fetch video information
        video_database = self._video_data
        category_data = self._category_data
        feed = self.api.videos(ids)

        # Add data to cache
        check_categories = True
        for video in feed[u"items"]:
            video_database[video[u"id"]] = video
            if check_categories and not video[u"snippet"][u"categoryId"] in category_data:
                self._update_category_cache()
                check_categories = False

    def _videos(self, channel_ids, video_ids, pagetoken=None):
        """ Process VideoIDs and return listitems in a generator

        Parameters
        ----------
        channel_ids : list of unicode
            List of all the channels that are associated with the videos.

        video_ids : list of unicode
            List of all the video to show.

        pagetoken : unicode, optional
            The token id for the next page.
        """

        # Fetch data caches
        channel_cache = self._channel_data.setdefault(u"channels", {})
        category_cache = self._category_data
        video_cache = self._video_data

        # Check for any missing cache
        fetch_channels = frozenset(filter(lambda channelid: channelid not in channel_cache, channel_ids))
        fetch_videos = frozenset(filter(lambda videoid: videoid not in video_cache, video_ids))
        multi_channel = len(frozenset(channel_ids)) > 1

        # Fetch any missing channel data
        if fetch_channels:
            self._update_channel_cache(fetch_channels)

        # Fetch any missing video data
        if fetch_videos:
            self._update_video_cache(fetch_videos)

        # Process videos
        local_int = int
        is_hd = youtube_hd(default=2)
        re_find = __import__("re").compile("(\d+)(\w)")
        is_related = str(u"videoid" in params).lower()
        for channelId, videoId in zip(channel_ids, video_ids):
            # Skip to the next video if no cached data was found or if the video is not public
            video_data = video_cache.get(videoId)
            if video_data is None:
                logger.debug("Skipping video %s: No cache data found", videoId)
                continue
            elif video_data[u"status"][u"privacyStatus"] != u"public":
                logger.debug("Skipping video %s: Marked as private", videoId)
                continue

            # Fetch video snippet & content_details
            snippet = video_data[u"snippet"]
            content_details = video_data[u"contentDetails"]

            # Create listitem object
            item = ListItem()

            # Add channel Fanart
            if channel_cache[channelId][u"fanart"]:
                item.art["fanart"] = channel_cache[channelId][u"fanart"]

            # Fetch video Image url
            item.art["thumb"] = snippet[u"thumbnails"][u"medium"][u"url"]

            # Fetch Title
            item.label = snippet[u"localized"][u"title"]

            # Fetch Description
            item.info["plot"] = snippet[u"localized"][u"description"]

            # Fetch Studio
            item.info["studio"] = snippet[u"channelTitle"]

            # Fetch Possible Date
            date = snippet[u"publishedAt"]
            item.info.date(date[:date.find("T")], "%Y-%m-%d")

            # Fetch Viewcount
            item.info["count"] = video_data[u"statistics"][u"viewCount"]

            # Fetch Category
            cat_id = snippet[u"categoryId"]
            if cat_id in category_cache:
                item.info["genre"] = category_cache[cat_id]

            # Set Quality and Audio Overlays
            item.stream.hd(is_hd if is_hd >= 1 and content_details[u"definition"] == u"hd" else 0)

            # Fetch Duration
            duration_str = content_details[u"duration"]
            duration_str = re_find.findall(duration_str)
            if duration_str:
                duration = 0
                for time, timeType in duration_str:
                    if timeType == "H":
                        duration += (local_int(time) * 3600)
                    elif timeType == "M":
                        duration += (local_int(time) * 60)
                    elif timeType == "S":
                        duration += (local_int(time))

                # Set duration
                item.info["duration"] = duration

            # Add Context item to link to related videos and youtube channel if required
            item.context.related(related, videoid=videoId, updatelisting=is_related)
            if multi_channel:
                item.context.add(playlist, u"Go to: %s" % snippet[u"channelTitle"], contentid=channelId)

            # Return the listitem
            url = build_video_url(video_data[u"id"])
            yield item.get_direct(url)

        # Add next Page entry if pagetoken is giving
        if pagetoken:
            yield ListItem.add_next(pagetoken=pagetoken)

        # Add playlists item to results
        if not multi_channel and u"pagetoken" not in params and params.get(u"enable_playlists", u"false") == u"true":
            item = ListItem()
            item.label = u"[B]%s[/B]" % localize("playlists")
            item.art["icon"] = "DefaultVideoPlaylists.png"
            item.art.global_thumb(u"youtube.png")
            item.url["contentid"] = channel_ids[0]
            yield item.get_tuple(playlists)

    def __init__(self):
        # Instantiate Youtube API
        self.api = API()
        cleanup_functions.append(self.cleanup)

    def playlists(self, content_id, show_all=False):
        """
        List all playlist for giving channel

        Parameters
        ----------
        content_id : unicode
            Channel uuid or channel name to list playlists for

        show_all : bool, optional(default=False)
            When True, a listitem linking to all of the channel videos will be available
        """

        # Fetch channel uuid
        channel_id = self._validate_uuid(content_id, playlist_uuid=False)

        # Fetch fanart image for channel
        channel_cache = self._channel_data.setdefault(u"channels", {})
        if channel_id in channel_cache:
            fanart = channel_cache[channel_id][u"fanart"]
        else:
            fanart = None

        # Fetch channel playlists feed
        feed = self.api.playlists(channel_id)

        # Display a link for listing all channel videos
        if show_all:
            title = u"[B]%s" % localize("all_videos")
            yield ListItem.add_youtube(channel_id, title, enable_playlists=False, wide_thumb=True)

        # Loop Entries
        for playlist_item in feed[u"items"]:
            # Create listitem object
            item = ListItem()

            # Fetch Video ID
            item.url["contentid"] = playlist_item[u"id"]

            # Fetch video snippet
            snippet = playlist_item[u"snippet"]

            # Fetch Title and Video Cound for combining Title
            item.label = u"%s (%s)" % (snippet[u"localized"][u"title"], playlist_item[u"contentDetails"][u"itemCount"])

            # Fetch Image Url
            item.art["thumb"] = snippet[u"thumbnails"][u"medium"][u"url"]

            # Set Fanart
            if fanart:
                item.art["fanart"] = fanart

            # Fetch Possible Plot and Check if Available
            item.info["plot"] = snippet[u"localized"][u"description"]

            # Fetch Possible Date and Check if Available
            date = snippet[u"publishedAt"]
            item.info.date(date[:date.find("T")], "%Y-%m-%d")

            # Add InfoLabels and Data to Processed List
            yield item.get_tuple(playlist)

    def related(self, video_id):
        """
        Search for all videos related to a giving video id

        Parameters
        ----------
        video_id : unicode
            ID of the video to fetch related videos for
        """
        video_list = []
        channel_list = []
        feed = self.api.search(params.get(u"pagetoken"), relatedToVideoId=video_id)
        for item in feed[u"items"]:
            channel_list.append(item[u"snippet"][u"channelId"])
            video_list.append(item[u"id"][u"videoId"])

        # List all the related videos
        return self._videos(channel_list, video_list, feed.get(u"nextPageToken"))

    def playlist(self, content_id):
        """
        List all video within youtube playlist

        Parameters
        ----------
        content_id : unicode
            Channel id or channel name or playlist id to list videos for.
        """

        # Fetch channel uploads uuid
        playlist_id = self._validate_uuid(content_id, playlist_uuid=True)

        # Fetch playlist feed
        feed = self.api.playlist_items(playlist_id, params.get("pagetoken"))
        channel_list = []
        video_list = []

        # Fetch video ids for all public videos
        for item in feed[u"items"]:
            channel_list.append(item[u"snippet"][u"channelId"])
            video_list.append(item[u"snippet"][u"resourceId"][u"videoId"])

        # Return the list of video listitems
        return self._videos(channel_list, video_list, feed.get(u"nextPageToken"))


class API(object):
    """
    API class to handle requests to the youtube v3 api

    Parameters
    ----------
    max_results : str, optional(default=50)
        The maxResults parameter specifies the maximum number of items that should be returned in the result set.

    pretty_print : str, optional(default="false")
        If True then the json response will be nicely indented.

    key : str, optional
        The key used to access the youtube api.
    """

    def __init__(self, max_results="50", pretty_print="false", key=None):
        self.language = youtube_lang(u"en")
        self.req_session = requests_session()
        self.default_params = {"maxResults": max_results,
                               "prettyPrint": pretty_print,
                               "key": key if key else "AIzaSyCR4bRcTluwteqwplIC34wEf0GWi9PbSXQ"}

    def _connect_v3(self, api_type, query, max_age=None):
        """
        Send API request and return response as a json object

        Parameters
        ----------
        api_type : str
            The type of api request to make.

        query : dict
            Dict of parameters that will be send to the api as a query.

        max_age : int, optional
            Max age override for the url cache.
        """

        # Check api_type of video id(s) before making request
        if "id" in query and hasattr(query["id"], '__iter__'):
            query["id"] = u",".join(query["id"])

        # Log the query debug log
        logger.debug("Youtube API Params for resource: %s", api_type)
        for key, value in query.iteritems():
            if key != "key":
                logger.debug("--- %-11s = %s", key, value)

        url = "https://www.googleapis.com/youtube/v3/%s" % api_type
        source = self.req_session.get(url, params=query, headers=None if max_age is None else {"x-max-age": max_age})
        response = json.loads(source.content, encoding=source.encoding)
        if u"error" not in response:
            return response
        else:
            try:
                message = response[u"error"]["errors"][0][u"message"]
            except:
                raise RuntimeError("Youtube V3 API return an error response")
            else:
                raise RuntimeError("Youtube V3 API return an error response: %s" % message)

    def channels(self, channel_id=None, for_username=None):
        """
        Return all available information for giving channel

        Parameters
        ----------
        channel_id : unicode or list of unicode, optional
            ID(s) of the channel for requesting data for.

        for_username : unicode, optional
            Username of the channel for requesting information for.

        Note
        ----
        If both parameters are giving then channel_id will take priority.
        """

        # Set parameters
        query = self.default_params.copy()
        query["fields"] = \
            u"items(id,brandingSettings/image/bannerTvMediumImageUrl," \
            u"contentDetails/relatedPlaylists/uploads,snippet/localized)"
        query["part"] = u"contentDetails,brandingSettings,snippet"
        query["hl"] = self.language

        # Add the channel_id or channel name of the channel to params
        if channel_id:
            query["id"] = channel_id
        elif for_username:
            query["forUsername"] = for_username
        else:
            raise ValueError("No valid Argument was giving for channels")

        # Connect to server and return json response
        return self._connect_v3("channels", query)

    def video_categories(self, cat_id=None, region_code="us"):
        """
        Return the categorie names for giving id(s)

        Parameters
        ----------
        cat_id : unicode, optinal
            ID(s) of the categories to fetch category names for.

        region_code : str, optional(defult="us")
            The region code for the categories ids

        Note
        ----
        If no id(s) are given then all category ids are fetched for given region.
        """

        # Set parameters
        query = self.default_params.copy()
        query["fields"] = u"items(id,snippet/title)"
        query["part"] = u"snippet"
        query["hl"] = self.language
        query["regionCode"] = region_code

        # Set mode of fetching, by id or region
        if cat_id:
            query["id"] = cat_id

        # Fetch video Information
        return self._connect_v3("videoCategories", query)

    def playlist_items(self, playlist_id, pagetoken=None):
        """
        Return all videos ids for giving playlist ID.

        Parameters
        ----------
        playlist_id : unicode
            ID of youtube playlist

        pagetoken : unicode
            The token for the next page of results
        """

        # Set parameters
        query = self.default_params.copy()
        query["fields"] = u"nextPageToken,items(snippet(channelId,resourceId/videoId))"
        query["part"] = u"snippet"
        query["playlistId"] = playlist_id

        # Add pageToken if exists
        if pagetoken:
            query["pageToken"] = pagetoken

        # Connect to server and return json response
        return self._connect_v3("playlistItems", query)

    def videos(self, video_id):
        """
        Return all available information for giving video/vidoes.

        Parameters
        ----------
        video_id : unicode or list of unicode
            Video id(s) to fetch data for.
        """

        # Set parameters
        query = self.default_params.copy()
        query["fields"] = u"items(id,snippet(publishedAt,channelId,thumbnails/medium/url,channelTitle," \
                          u"categoryId,localized),contentDetails(duration,definition),statistics/viewCount," \
                          u"status/privacyStatus)"
        query["part"] = u"contentDetails,statistics,snippet,status"
        query["hl"] = self.language
        query["id"] = video_id

        # Connect to server and return json response
        return self._connect_v3("videos", query)

    def playlists(self, channel_id):
        """
        Return all playlist for a giving channel_id.

        Parameters
        ----------
        channel_id : unicode
            Id of the channel to fetch playlists for.
        """

        # Set Default parameters
        query = self.default_params.copy()
        query["fields"] = u"nextPageToken,items(id,contentDetails/itemCount,snippet" \
                          u"(publishedAt,localized,thumbnails/medium/url))"
        query["part"] = u"snippet,contentDetails"
        query["channelId"] = channel_id

        # Connect to server and return json response
        feed = self._connect_v3("playlists", query)
        pagetoken = feed.get(u"nextPageToken")

        # Loop all pages
        while pagetoken:
            query["pageToken"] = pagetoken
            next_feed = self._connect_v3("playlists", query)
            feed[u"items"].extend(next_feed[u"items"])
            pagetoken = next_feed.get(u"nextPageToken")

        # Return all playlists
        feed[u"nextPageToken"] = None
        return feed

    def search(self, pagetoken=None, **search_params):
        """
        Return any search results.

        Parameters
        ----------
        pagetoken : unicode, optional
            The token for the next page of results.

        search_params : dict
            Youtube API search Parameters, refer to "https://developers.google.com/youtube/v3/docs/search/"
        """

        # Set Default parameters
        query = self.default_params.copy()
        query["fields"] = u"nextPageToken,items(id/videoId,snippet/channelId)"
        query["relevanceLanguage"] = self.language
        query["safeSearch"] = u"none"
        query["part"] = u"snippet"
        query["type"] = u"video"
        query.update(search_params)

        # Add pageToken if needed
        if pagetoken:
            query["pageToken"] = pagetoken

        # Connect to server and return json response
        return self._connect_v3("search", query)
