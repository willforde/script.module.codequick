# -*- coding: utf-8 -*-

# Standard Library Imports
import logging
import json
import os

# Package imports
from .base import logger_id
from .storage import PersistentDict
from .api import register_route, register_resolver, Route
from .support import CacheProperty
from .listing import Listitem

# Outer package imports
import urlquick

# Logger specific to this module
logger = logging.getLogger("%s.youtube" % logger_id)

# Localized string Constants
ALL_VIDEOS = 16100
PLAYLISTS = 136


class API(object):
    """
    API class to handle requests to the youtube v3 api

    :param int max_results: (Optional) The maximum number of items per page that should be returned. (default => 50)
    :param bool pretty_print: (Optional) If True then the json response will be nicely indented. (default => False)
    """

    def __init__(self, max_results=50, pretty_print=False):
        self.req_session = urlquick.Session(raise_for_status=True)
        self.req_session.params = {"maxResults": str(max_results),
                                   "prettyPrint": str(pretty_print).lower(),
                                   "key": "AIzaSyCR4bRcTluwteqwplIC34wEf0GWi9PbSXQ"}

    def _connect_v3(self, api_type, query):
        """
        Send API request and return response as a json object.

        :param str api_type: The type of api request to make.
        :param dict query: Dictionary of parameters that will be send to the api as a query.

        :returns: The youtube api response as a dictionary.
        :rtype: dict

        :raises RuntimeError: If youtube returns a error response.
        """
        # Convert id query from a list, to a comma separated list of id's, if required
        if "id" in query and hasattr(query["id"], '__iter__'):
            query["id"] = u",".join(query["id"])

        # Download the resource from the youtube v3 api
        url = "https://www.googleapis.com/youtube/v3/%s" % api_type
        source = self.req_session.get(url, params=query)
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

        Note:
        If both parameters are given, then channel_id will take priority.

        Refer to 'https://developers.google.com/youtube/v3/docs/channels/list'

        :param channel_id: (Optional) ID(s) of the channel for requesting data for.
        :type channel_id: str or unicode or list or frozenset

        :param for_username: (Optional) Username of the channel for requesting information for.
        :type for_username: unicode or str

        :returns: Dictionary of channel information.
        :rtype: dict

        :raises ValueError: If neither channel_id or for_username is given.
        """
        # Set parameters
        query = {"hl": "en", "part": "contentDetails,brandingSettings,snippet",
                 "fields": u"items(id,brandingSettings/image/bannerTvMediumImageUrl,"
                           u"contentDetails/relatedPlaylists/uploads,snippet/localized)"}

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

        Refer to 'https://developers.google.com/youtube/v3/docs/videoCategories/list'

        Note:
        If no id(s) are given then all category ids are fetched for given region.

        :param cat_id: (Optional) ID(s) of the categories to fetch category names for.
        :type cat_id: str or unicode or list or frozenset

        :param region_code: (Optional) The region code for the categories id(s).
        :type region_code: str or unicode

        :returns: Dictionary of video categories.
        :rtype: dict
        """
        # Set parameters
        query = {"fields": u"items(id,snippet/title)", "part": "snippet", "hl": "en", "regionCode": region_code}

        # Set mode of fetching, by id or region
        if cat_id:
            query["id"] = cat_id

        # Fetch video Information
        return self._connect_v3("videoCategories", query)

    def playlist_items(self, playlist_id, pagetoken=None):
        """
        Return all videos ids for giving playlist ID.

        Refer to 'https://developers.google.com/youtube/v3/docs/playlistItems/list'

        :param playlist_id: ID of youtube playlist
        :type playlist_id: str or unicode

        :param pagetoken: The token for the next page of results
        :type pagetoken: str or unicode

        :returns: Dictionary of playlist items.
        :rtype: dict
        """
        # Set parameters
        query = {"fields": u"nextPageToken,items(snippet(channelId,resourceId/videoId))", "part": u"snippet",
                 "playlistId": playlist_id}

        # Add pageToken if exists
        if pagetoken:
            query["pageToken"] = pagetoken

        # Connect to server and return json response
        return self._connect_v3("playlistItems", query)

    def videos(self, video_id):
        """
        Return all available information for giving video/vidoes.

        Refer to 'https://developers.google.com/youtube/v3/docs/videos/list'

        :param video_id: Video id(s) to fetch data for.
        :type video_id: str or unicode or list or frozenset

        :returns: Dictionary of video items.
        :rtype: dict
        """
        # Set parameters
        query = {"part": u"contentDetails,statistics,snippet,status", "hl": "en", "id": video_id,
                 "fields": u"items(id,snippet(publishedAt,channelId,thumbnails/medium/url,channelTitle,"
                           u"categoryId,localized),contentDetails(duration,definition),statistics/viewCount,"
                           u"status/privacyStatus)"}

        # Connect to server and return json response
        return self._connect_v3("videos", query)

    def playlists(self, channel_id):
        """
        Return all playlist for a giving channel_id.

        Refer to 'https://developers.google.com/youtube/v3/docs/playlists/list'

        :param channel_id: Id of the channel to fetch playlists for.
        :type channel_id: str or unicode

        :returns: Dictionary of playlists.
        :rtype: dict
        """
        # Set Default parameters
        query = {"part": u"snippet,contentDetails", "channelId": channel_id,
                 "fields": u"nextPageToken,items(id,contentDetails/itemCount,snippet"
                           u"(publishedAt,localized,thumbnails/medium/url))"}

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

    def search(self, **search_params):
        """
        Return any search results.

        Refer to 'https://developers.google.com/youtube/v3/docs/search/list' for search Parameters

        :param search_params: Keyword arguments of Youtube API search Parameters

        :returns: Dictionary of search results.
        :rtype: dict
        """
        # Set Default parameters
        query = {"relevanceLanguage": "en", "safeSearch": u"none", "part": u"snippet", "type": "video",
                 "fields": u"nextPageToken,items(id/videoId,snippet/channelId)"}

        # Add the search params to query
        query.update(search_params)

        # Connect to server and return json response
        return self._connect_v3("search", query)


class APIControl(Route):
    """Class to control the access to the youtube API."""

    def __init__(self):
        super(APIControl, self).__init__()

        self.api = API()
        """:class:`API`: Class for handling api requests"""

    def cache_cleanup(self):
        """Trim down the cache if cache gets too big."""
        logger.debug("Running Youtube Cache Cleanup")
        video_cache = self.video_cache
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

        # Remove 1000 of the oldest videos
        for count, (published, videoid, channelid) in enumerate(sorted_cache):
            if count < 1000:
                remove_list.append(videoid)
            else:
                # Sense cached item was not removed, mark the channelid as been referenced
                valid_channel_refs.add(channelid)

        # If there are any videos to remove then remove them and also remove any unreferenced channels
        if remove_list:
            # Remove all video that are marked for removel
            for videoid in remove_list:
                logger.debug("Removing cached video : '%s'", videoid)
                del video_cache[videoid]

            # Clean the channel cache of unreferenced channel ids
            channel_cache = self.channel_cache.get(u"channels", {})
            for channelid in channel_cache.keys():
                if channelid not in valid_channel_refs:
                    del channel_cache[channelid]

            # Clean the chanel ref cache of unreferenced channel ids
            ref_cache = self.channel_cache.get(u"ref", {})
            for key, channelid in ref_cache.iteritems():
                if channelid not in valid_channel_refs:
                    del ref_cache[key]

            # Close connection to channel cache
            channel_cache.close()

        # Close connection to cache database
        video_cache.close()

    @CacheProperty
    def category_cache(self):
        """
        Return category_data database.

        :returns: The category_data database
        :rtype: dict
        """
        dir_path = os.path.join(self.get_info("profile_global"), u"youtube")
        return PersistentDict(u"category_data.json", dir_path)

    @CacheProperty
    def channel_cache(self):
        """
        Return channel_data database.

        :returns: The channel_data database.
        :rtype: dict
        """
        dir_path = os.path.join(self.get_info("profile"), u"youtube")
        return PersistentDict(u"channel_data.json", dir_path)

    @CacheProperty
    def video_cache(self):
        """
        Return video_data database.

        :returns: The video_data database.
        :rtype: dict
        """
        from shelve import DbfilenameShelf
        filepath = os.path.join(self.get_info("profile"), u"youtube", u"video_data.shelf")
        video_cache = DbfilenameShelf(filepath, protocol=-1, writeback=False)

        # Mark the video_cache for cleanup when video count is greater than 2000
        if len(video_cache) > 2000:
            self.register_callback(self.cache_cleanup)

        return video_cache

    def validate_uuid(self, contentid, require_playlist=True):
        """
        Convert contentid to a channel/upload/playlist id, depending on require_playlist state.

        Content Type        | playlist_id = False         | playlist_id = True
        ----------------------------------------------------------------------
        Channel Name        | Channel ID                  | Uploads ID
        Channel ID          | Channel ID                  | Uploads ID
        Channel Uploads ID  | Channel ID                  | Uploads ID
        Playlist ID         | ValueError                  | Playlist ID
        
        :type contentid: unicode
        :param contentid: ID of youtube content to validate, Channel Name, Channel ID,
                          Channel Uploads ID or Playlist ID.
        
        :type require_playlist: bool
        :param require_playlist: (Optional) True, return a upload/playlist ID (Default). False, return a channelID.

        :raises ValueError: Will be raised if content id is a playlist id and require_playlist is False.
                            Sense we can not match a playlist id to a channel id. ValueError can also be raised
                            if there is no mapping from a uploads id to a channel id.
        """
        # Quick Access Vars
        content_code = contentid[:2]
        channel_cache = self.channel_cache
        channel_refs = channel_cache.setdefault(u"ref", {})
        channel_data = channel_cache.setdefault(u"channels", {})

        # Directly return the content id if its a playlistID or uploadsID and playlist_uuid is required
        if content_code == u"PL" or content_code == u"FL":
            if require_playlist:
                return contentid
            else:
                raise ValueError("Unable to link a playlist uuid to a channel uuid")

        # Return the channel uploads uuid if playlist_uuid is required else the channels uuid if we have a mapping for
        # said uploads uuid. Raises ValueError when unable to map the uploads uuid to a channel.
        elif content_code == u"UU":
            if require_playlist:
                return contentid
            elif contentid in channel_refs:
                return channel_refs[contentid]
            else:
                raise ValueError("Unable to link a channel uploads uuid to a channel uuid")

        # Check if content is a channel id
        elif content_code == u"UC":
            # Return the channel uuid as is if playlist_uuid is not required
            if require_playlist is False:
                return contentid

            # Extract channel upload id fom cache
            elif contentid in channel_data:
                return channel_data[contentid][u"uploads"]

            # Request channel data from server and return channels uploads uuid
            else:
                self.update_channel_cache(channel_id=contentid)
                return channel_data[contentid][u"uploads"]

        else:
            # If we get here then content id must be a channel name
            if contentid in channel_refs:
                # Extract the channel id from cache
                channelid = channel_refs[contentid]
                if channelid not in channel_data:
                    self.update_channel_cache(channel_id=channelid)
            else:
                self.update_channel_cache(for_username=contentid)
                channelid = channel_refs[contentid]

            # Return the channel uploads uuid if playlist uuid is required else return the channel uuid
            if require_playlist:
                return channel_data[channelid][u"uploads"]
            else:
                return channelid

    def update_channel_cache(self, channel_id=None, for_username=None):
        """
        Update on disk cache of channel information

        :param channel_id: (Optional) ID of the channel to request information for.
        :type channel_id: str or unicode or list or frozenset

        :param for_username: (Optional) Username of the channel to request information for.
        :type for_username: str or unicode

        Note:
        If both channel_id and for_username is given then channel_id will take priority.
        """
        # Make channels api request
        feed = self.api.channels(channel_id, for_username)

        # Fetch channel cache
        channel_cache = self.channel_cache
        channel_refs = channel_cache.setdefault(u"ref", {})
        channel_data = channel_cache.setdefault(u"channels", {})

        # Update cache
        for item in feed[u"items"]:
            # Fetch common info
            data = {u"title": item[u"snippet"][u"localized"][u"title"],
                    u"description": item[u"snippet"][u"localized"][u"description"],
                    u"uploads": item[u"contentDetails"][u"relatedPlaylists"][u"uploads"]}

            # Fetch the channel banner if available
            try:
                data[u"fanart"] = item[u"brandingSettings"][u"image"][u"bannerTvMediumImageUrl"]
            except KeyError:
                data[u"fanart"] = None

            # Set and save channel info into cache
            channel_data[item[u"id"]] = data
            channel_refs[data[u"uploads"]] = item[u"id"]

        # Also add reference for channel name if given
        if for_username:
            channelid = feed[u"items"][0][u"id"]
            channel_refs[for_username] = channelid
            logger.debug("Channel ID for channel '%s' is '%s'", for_username, channelid)

        # Sync cache to disk
        channel_cache.flush()

    def update_category_cache(self, cat_id=None):
        """
        Update on disk cache of category information

        :param cat_id: (Optional) ID(s) of the categories to fetch category names for.
        :type cat_id: unicode or list or frozenset

        Note:
        If no category id is given then all categories names will be fetched.
        """
        # Fetch category Information
        feed = self.api.video_categories(cat_id)

        # Update category cache
        category_data = self.category_cache
        for item in feed[u"items"]:
            category_data[item[u"id"]] = item[u"snippet"][u"title"]
        category_data.flush()

    def update_video_cache(self, ids):
        """
        Update on disk cache of video information

        :param ids: ID(s) of videos to fetch information for.
        :type ids: unicode or list or frozenset
        """
        # Fetch video information
        video_database = self.video_cache
        category_data = self.category_cache
        feed = self.api.videos(ids)

        # Add data to cache
        check_categories = True
        for video in feed[u"items"]:
            video_database[video[u"id"].encode("utf8")] = video
            if check_categories and not video[u"snippet"][u"categoryId"] in category_data:
                self.update_category_cache()
                check_categories = False

    def videos(self, channel_ids, video_ids, pagetoken=None, enable_playlists=True):
        """
        Process VideoIDs and return listitems in a generator

        :param channel_ids: List of all the channels that are associated with the videos.
        :type channel_ids: list

        :param video_ids: List of all the videos to show.
        :type video_ids: list

        :param pagetoken: (Optional) The token id for the next page.
        :type pagetoken: unicode

        :param enable_playlists: (Optional) Set to True to enable linking to channel playlists. (default => False)
        :type enable_playlists: bool

        :returns: A generator of listitems.
        :rtype: :class:`types.GeneratorType`
        """
        # Fetch data caches
        channel_cache = self.channel_cache.setdefault(u"channels", {})
        category_cache = self.category_cache
        video_cache = self.video_cache

        # Check for any missing cache
        fetch_channels = frozenset(filter(lambda channelid: channelid not in channel_cache, channel_ids))
        fetch_videos = frozenset(filter(lambda videoid: videoid not in video_cache, video_ids))
        multi_channel = len(frozenset(channel_ids)) > 1

        # Fetch any missing channel data
        if fetch_channels:
            self.update_channel_cache(fetch_channels)

        # Fetch any missing video data
        if fetch_videos:
            self.update_video_cache(fetch_videos)

        # Check that the quality setting is set to HD or greater
        try:
            ishd = self.setting.get_int("video_quality", addon_id="script.module.youtube.dl")
        except RuntimeError:
            ishd = True

        # Process videos
        duration_search = __import__("re").compile("(\d+)(\w)")
        for channel_id, video_id in zip(channel_ids, video_ids):
            # Skip to the next video if no cached data was found or if the video is not public
            video_data = video_cache.get(video_id)
            if video_data is None:
                logger.debug("Skipping video '%s': No cache data found", video_id)
                continue
            elif video_data[u"status"][u"privacyStatus"] != u"public":
                logger.debug("Skipping video '%s': Marked as private", video_id)
                del video_cache[video_id]
                continue

            # Create listitem object
            item = Listitem()

            # Fetch video snippet & content_details
            snippet = video_data[u"snippet"]
            content_details = video_data[u"contentDetails"]

            # Fetch Title
            item.label = snippet[u"localized"][u"title"]

            # Add channel Fanart
            item.art["fanart"] = channel_cache[channel_id][u"fanart"]

            # Fetch video Image url
            item.art["thumb"] = snippet[u"thumbnails"][u"medium"][u"url"]

            # Fetch Description
            item.info["plot"] = snippet[u"localized"][u"description"]

            # Fetch Studio
            item.info["studio"] = snippet[u"channelTitle"]

            # Fetch Viewcount
            item.info["count"] = video_data[u"statistics"][u"viewCount"]

            # Fetch Possible Date
            date = snippet[u"publishedAt"]
            item.info.date(date[:date.find("T")], "%Y-%m-%d")

            # Fetch Category
            cat_id = snippet[u"categoryId"]
            if cat_id in category_cache:
                item.info["genre"] = category_cache[cat_id]

            # Set Quality and Audio Overlays
            item.stream.hd(bool(content_details[u"definition"] == u"hd" and ishd))

            # Fetch Duration
            duration_str = content_details[u"duration"]
            duration_str = duration_search.findall(duration_str)
            if duration_str:
                duration = 0
                for time_segment, timeType in duration_str:
                    if timeType == "H":
                        duration += (int(time_segment) * 3600)
                    elif timeType == "M":
                        duration += (int(time_segment) * 60)
                    elif timeType == "S":
                        duration += (int(time_segment))

                # Set duration
                item.info["duration"] = duration

            # Add Context item to link to related videos
            item.context.related(Related, video_id=video_id)

            # Add Context item for youtube channel if videos from more than one channel are ben listed
            if multi_channel:
                item.context.container(u"Go to: %s" % snippet[u"channelTitle"], Playlist, contentid=channel_id)

            # Return the listitem
            item.set_callback(play_video, video_id=video_id)
            yield item

        # Add next Page entry if pagetoken is giving
        if pagetoken:
            yield Listitem.next_page(pagetoken=pagetoken)

        # Add playlists item to results
        if enable_playlists and not multi_channel and pagetoken is None:
            item = Listitem()
            item.label = u"[B]%s[/B]" % self.localize(PLAYLISTS)
            item.art["icon"] = "DefaultVideoPlaylists.png"
            item.art.global_thumb(u"youtube.png")
            item.set_callback(Playlists, contentid=channel_ids[0], show_all=False)
            yield item


@register_route
class Playlist(APIControl):
    def run(self, contentid, pagetoken=None, enable_playlists=True, loop=False):
        """
        List all video within youtube playlist

        :param contentid: Channel id, channel name or playlist id to list videos for.
        :type contentid: unicode

        :param pagetoken: (Optional) The page token representing the next page of content.
        :type pagetoken: unicode

        :param enable_playlists: (Optional) Set to True to enable linking to channel playlists. (default => False)
        :type enable_playlists: bool

        :param loop: (Optional) Return all the videos within playlist. (Default => False)
        :type loop: bool

        :returns: A generator of listitems.
        :rtype: :class:`types.GeneratorType`
        """
        # Fetch channel uploads uuid
        playlist_id = self.validate_uuid(contentid, require_playlist=True)
        all_listitems = []

        while True:
            # Fetch playlist feed
            feed = self.api.playlist_items(playlist_id, pagetoken)
            pagetoken = feed.get(u"nextPageToken")
            channel_list = []
            video_list = []

            # Fetch video ids for all public videos
            for item in feed[u"items"]:
                channel_list.append(item[u"snippet"][u"channelId"])
                video_list.append(item[u"snippet"][u"resourceId"][u"videoId"].encode("utf8"))

            if loop:
                # Fetch the list of video listitems
                listitems = self.videos(channel_list, video_list, enable_playlists=False)
                all_listitems.extend(listitems)
                # Return all listitems when no more page tokens are found
                if not pagetoken:
                    return all_listitems
            else:
                # Return the list of video listitems
                return self.videos(channel_list, video_list, pagetoken, enable_playlists)


@register_route
class Playlists(APIControl):
    def run(self, content_id, show_all=True):
        """
        List all playlist for giving channel

        :param content_id: Channel uuid or channel name to list playlists for
        :type content_id: unicode

        :param show_all: (Optional) Add link to all of the channels videos if True. (default => True)
        :type show_all: bool

        :returns: A generator of listitems.
        :rtype: :class:`types.GeneratorType`
        """
        # Fetch channel uuid
        channel_id = self.validate_uuid(content_id, require_playlist=False)

        # Fetch fanart image for channel
        channel_cache = self.channel_cache.setdefault(u"channels", {})
        if channel_id in channel_cache:
            fanart = channel_cache[channel_id][u"fanart"]
        else:
            fanart = None

        # Fetch channel playlists feed
        feed = self.api.playlists(channel_id)

        # Display a link for listing all channel videos
        if show_all:
            title = self.localize(ALL_VIDEOS)
            yield Listitem.youtube(channel_id, title, enable_playlists=False, wide_thumb=True)

        # Loop Entries
        for playlist_item in feed[u"items"]:
            # Create listitem object
            item = Listitem()

            # Fetch video snippet
            snippet = playlist_item[u"snippet"]

            # Fetch Title and Video Cound for combining Title
            label = u"%s (%s)" % (snippet[u"localized"][u"title"], playlist_item[u"contentDetails"][u"itemCount"])
            item.label = label

            # Fetch Image Url
            item.art["thumb"] = snippet[u"thumbnails"][u"medium"][u"url"]

            # Set Fanart
            item.art["fanart"] = fanart

            # Fetch Possible Plot and Check if Available
            item.info["plot"] = snippet[u"localized"][u"description"]

            # Add InfoLabels and Data to Processed List
            item.set_callback(Playlist, contentid=playlist_item[u"id"], enable_playlists=False)
            yield item


@register_route
class Related(APIControl):
    def run(self, video_id, pagetoken=None):
        """
        Search for all videos related to a giving video id.

        :param video_id: Id of the video the fetch related video for.
        :type video_id: unicode

        :param pagetoken: (Optional) The page token representing the next page of content.
        :type pagetoken: unicode

        :returns: A generator of listitems.
        :rtype: :class:`types.GeneratorType`
        """
        video_list = []
        channel_list = []
        self.update_listing = True
        feed = self.api.search(pageToken=pagetoken, relatedToVideoId=video_id)
        for item in feed[u"items"]:
            channel_list.append(item[u"snippet"][u"channelId"])
            video_list.append(item[u"id"][u"videoId"].encode("utf8"))

        # List all the related videos
        return self.videos(channel_list, video_list, pagetoken=feed.get(u"nextPageToken"))


@register_resolver
def play_video(plugin, video_id):
    """
    :type plugin: :class:`codequick.PlayMedia`
    :type video_id: unicode
    """
    url = "https://www.youtube.com/watch?v=%s" % video_id
    return plugin.extract_source(url)
