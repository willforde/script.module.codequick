# Standard Library Imports
import os
import json

# Package imports
from .inheritance import VirtualFS, PlayMedia
from .api import route, localized

# Prerequisites
localized({"Go_to_channel": 32902, "playlists": 136, "All_videos": 16100})


@route("/internal/youtube/playlist")
class YTPlaylist(VirtualFS):
    """ List all videos in a playlist """

    def start(self):
        gdata = APIControl(self)
        if "playlistid" in self:
            return gdata.playlist(playlist_id=self[u"playlistid"])
        else:
            return gdata.playlist(content_id=self[u"contentid"])


@route("/internal/youtube/playlists")
class YTPlaylists(VirtualFS):
    """ List all the playlists of a channel """

    def start(self):
        if "channelid" in self:
            return self._initiate(channel_id=self[u"channelid"])
        else:
            return self._initiate(content_id=self[u"contentid"])

    def _initiate(self, content_id=None, channel_id=None):
        gdata = APIControl(self)
        return list(gdata.playlists(content_id, channel_id))


@route("/internal/youtube/related")
class YTRelated(VirtualFS):
    """ List all videos that are related to a video id """

    def start(self):
        gdata = APIControl(self)
        return gdata.related(self[u"videoid"])


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
    channel, as well as linking the the channels uploads, shown as "All videos"

    To use just subclass this class and set the required property that points to the youtube content

    content_id : string or unicode --- Channel ID or Channel Name to list playlists for, usefull when unsure of the type
    channel_id : string or unicode --- ID of the channel to list playlists for when the channel ID is known

    Can set any one of the 2 propertys, but not both, if both are given then channel_id has priority
    -------------------------------------------
    @codequick.route("/")
    class Root(codequick.YoutubeBase):
        channel_id = "UCnavGPxEijftXneFxk28srA"
    """
    channel_id = content_id = None

    def start(self):
        if self.channel_id is not None:
            results = self._initiate(channel_id=self.channel_id)
            results.append(self.listitem.add_youtube(self.channel_id, label=self.get_local_string("All_videos"),
                                                     enable_playlists=False, wide_thumb=True))
        elif self.content_id is not None:
            results = self._initiate(content_id=self.content_id)
            results.append(self.listitem.add_youtube(self.content_id, label=self.get_local_string("All_videos"),
                                                     enable_playlists=False, wide_thumb=True))
        else:
            raise ValueError("No Content ID was set for addon to work")

        return results


class APIControl(object):
    """ Class to control the access to the youtube API """

    __video_data = __channel_data = __category_data = None

    def __del__(self):
        """ Trim down the cache if cache gets too big """

        # Fetch data caches
        if not self.__video_data or not self.__channel_data:
            return None
        video_cache = self.__video_data
        channel_cache = self.__channel_data
        force_sync = False

        # Cut down the size of the video cache if it get larger than 2000 items
        cache_len = len(video_cache)
        remove_count = cache_len - 500
        if cache_len > 2000:
            self.base.debug("Running Youtube Cache Cleanup")
            video_cache.writeback = True
            for count, element in enumerate(
                    sorted(((videoID, data[u"snippet"][u"publishedAt"]) for videoID, data in video_cache.iteritems()),
                           key=lambda data: data[1])):
                if count < remove_count:
                    del video_cache[element[0]]
                else:
                    break

            # Remove any channel cache item that no longer referenced by the video cache
            if len(channel_cache) > 10:
                channels_left = {data[u"snippet"][u"channelId"] for data in video_cache.itervalues()}
                for channelID in channel_cache.keys():
                    if channelID not in channels_left:
                        del channel_cache[channelID]
                        force_sync = True

        # Synchronize data to disk if needed and close connection to file
        channel_cache.close(force_sync)
        video_cache.close()

    def __init__(self, base):
        self.base = base
        req_session = base.request_basic(60 * 4)
        language = base.utils.youtube_lang(u"en")
        self.api = API(req_session, lang=language)

    @property
    def _category_data(self):
        """ Return opened category_data database or connect to the category_data database and return """
        if self.__category_data is not None:
            return self.__category_data
        else:
            dir_path = os.path.join(self.base.profile_global, "youtube")
            category_data = self.base.dict_storage("category_data.json", custom_dir=dir_path)
            self.__category_data = category_data
            return category_data

    @property
    def _channel_data(self):
        """ Return opened channel_data database or connect to the channel_data database and return """
        if self.__channel_data is not None:
            return self.__channel_data
        else:
            dir_path = os.path.join(self.base.profile, "youtube")
            channel_data = self.base.dict_storage("channel_data.json", custom_dir=dir_path)
            self.__channel_data = channel_data
            return channel_data

    @property
    def _video_data(self):
        """ Return opened video_data database or connect to the video_data database and return """
        if self.__video_data is not None:
            return self.__video_data
        else:
            dir_path = os.path.join(self.base.profile, "youtube")
            video_data = self.base.shelf_storage("video_data.shelf", custom_dir=dir_path)
            self.__video_data = video_data
            return video_data

    def _check_content_id(self, content_id, return_playlist_id=True):
        """
        Check the type of content_id we have and return the required ID for wanted type

        Args:
            content_id (basestring): ID of Youtube content to add, Channel Name, Channel ID, Channel Uploads ID or
                                     Playlist ID
            return_playlist_id (bool): True to return a playlistID/uploadID or False for channelID (default True)
        """

        # Fetch the channel cache object
        channel_data = self._channel_data

        # Return if content is a playlistID or uploadsID
        if content_id[:2] == "UU" or content_id[:2] == "PL":
            if return_playlist_id:
                return content_id
            else:
                raise ValueError("ContentID is not a valid ID for wanted type: %s" % content_id)

        # If channel id then either return it or fetch the playlistID for channel
        elif content_id[:2] == "UC":
            if not return_playlist_id:
                return content_id
            else:
                if content_id not in channel_data:
                    self.update_channel_cache(channel_id=content_id)
                return channel_data[content_id]["playlistID"]

        # ContentID must be a channel name so fetch the channelID and uploadsID
        else:
            channel_id = self.base.get_setting(content_id)
            if not channel_id or (return_playlist_id and channel_id not in channel_data):
                channel_id = self.update_channel_cache(for_username=content_id)
                if not channel_id:
                    self.base.set_setting(content_id, channel_id)

            if return_playlist_id:
                return channel_data[channel_id]["playlistID"]
            else:
                return channel_id

    def update_channel_cache(self, channel_id=None, for_username=None):
        """
        Update on disk cache of channel information

        channel_id : list or string or unicode --- ID of the channel for requesting infomation for.
        for_username : string or unicode --- Username of the channel for requesting information for.
        """

        # Fetch cache object
        channel_data = self._channel_data

        # Connect to API server and Fetch response
        feed = self.api.channels(channel_id, for_username)

        # Update the cache Title, Description, playlistID and fanart
        for item in feed[u"items"]:
            title = item[u"snippet"][u"localized"][u"title"]
            description = item[u"snippet"][u"localized"][u"description"]
            playlist_id = item[u"contentDetails"][u"relatedPlaylists"][u"uploads"]
            if u"brandingSettings" in item:
                fanart = item[u"brandingSettings"][u"image"][u"bannerTvMediumImageUrl"]
            else:
                fanart = None
            data = {"title": title, "description": description, "playlistID": playlist_id, "fanart": fanart}
            channel_data[item[u"id"]] = data

        # Sync cache to disk
        channel_data.sync()

        # Return the Channel ID of the first item, needed when using for_username
        if for_username:
            return feed[u"items"][0][u"id"]
        else:
            return None

    def update_category_cache(self, cat_id=None):
        """
        Update on disk cache of category information

        [cat_id] : list or string or unicode --- ID(s) of the categories to fetch category names for. (default None)
        """

        # Fetch category Information
        feed = self.api.video_categories(cat_id)

        # Update category cache
        category_data = self._category_data
        for item in feed[u"items"]:
            category_data[item[u"cat_id"]] = item[u"snippet"][u"title"]
        category_data.sync()

    def update_video_cache(self, ids):
        """
        Update on disk cache of video information

        ids : list or string or unicode --- ID(s) of videos to fetch information for
        """

        # Fetch video information
        video_database = self._video_data
        category_data = self._category_data
        feed = self.api.videos(ids)

        # Add data to cache
        check_categories = True
        for video in feed[u"items"]:
            video_database[video["ids"]] = video
            if check_categories and not video["snippet"]["categoryId"] in category_data:
                self.update_category_cache()
                check_categories = False

    def playlists(self, content_id=None, channel_id=None):
        """
        List all playlist for giving channel

        Can pass in any one of the 2 arguments, but if both are giving then channel_id has priority

        Args:
            content_id (basestring): Channel ID or Channel Name to list playlists for, usefull when unsure of the type
            channel_id (basestring): ID of the channel to list playlists for when the channel ID is known
        """

        # Fetch channel ID
        if content_id:
            channel_id = self._check_content_id(content_id, return_playlist_id=False)
        elif not channel_id:
            raise ValueError("No valid argument giving for youtube:playlists")
        feed = self.api.playlists(channel_id)

        # Fetch data caches
        channel_cache = self._channel_data
        if channel_id in channel_cache:
            fanart = channel_cache[channel_id]["fanart"]
        else:
            fanart = None

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
            item.set_thumb(snippet[u"thumbnails"][u"medium"][u"url"])

            # Set Fanart
            if fanart:
                item.set_fanart(fanart)

            # Fetch Possible Plot and Check if Available
            item.info("plot", snippet[u"localized"][u"description"])

            # Fetch Possible Date and Check if Available
            date = snippet[u"publishedAt"]
            item.set_date(date[:date.find("T")], "%Y-%m-%d")

            # Add InfoLabels and Data to Processed List
            yield item.get(YTPlaylist)

    def related(self, video_id):
        """
        search for all videos related to a giving video id

        video_id : string or unicode --- ID of the video to fetch related video for
        """

        # Fetch search results
        feed = self.api.search(self.base.get("pagetoken"), relatedToVideoId=video_id)
        video_list = [(video[u"snippet"][u"channelId"], video[u"id"][u"videoId"]) for video in feed["items"]]
        return self._videos(video_list, feed.get(u"nextPageToken"))

    def playlist(self, content_id=None, playlist_id=None):
        """
        List all video within youtube playlist

        [content_id] : string or unicode --- Channel ID / Channel Name or Playlist ID to list videos for, usefull when
                                             unsure of the type
        [playlist_id] : string or unicode --- ID of the channel to list videos for when the playlist ID is known

        Can pass in any one of the 2 arguments, but if both are giving then playlist_id has priority
        """

        # Connect to API server and Fetch response
        if content_id:
            playlist_id = self._check_content_id(content_id, return_playlist_id=True)
        elif not playlist_id:
            raise ValueError("No valid argument giving for youtube:playlist")
        feed = self.api.playlist_items(playlist_id, self.base.get("pagetoken"))
        video_list = []
        for item in feed[u"items"]:
            if item[u"status"][u"privacyStatus"] == u"public":
                data = (item[u"snippet"][u"channelId"], item[u"snippet"][u"resourceId"][u"videoId"])
                video_list.append(data)
        return self._videos(video_list, feed.get(u"nextPageToken"))

    def _videos(self, video_ids, pagetoken=None):
        """ Process VideoIDs and return listitems in a generator """

        # Check if video_ids is a valid list
        if not video_ids:
            raise ValueError("No valid list of video IDs ware giving")

        # Fetch data caches
        video_cache = self._video_data
        category_cache = self._category_data
        channel_cache = self._channel_data

        # Check for any missing data
        channel_ids = set()
        fetch_videos = set()
        fetch_channels = set()
        for channelID, videoId in video_ids:
            if channelID not in channel_cache:
                fetch_channels.add(channelID)
            if videoId not in video_cache:
                fetch_videos.add(videoId)
            channel_ids.add(channelID)

        # Fetch any missing data
        if fetch_channels:
            self.update_channel_cache(channel_id=fetch_channels)
        if fetch_videos:
            self.update_video_cache(fetch_videos)

        # Fetch Youtube Video Quality Setting
        is_hd = self.base.utils.youtube_hd(default=2)

        # Process videos
        local_int = int
        listitem = self.base.listitem
        re_find = __import__("re").findall
        is_related = str(u"videoid" in self.base).lower()
        for channelID, videoId in video_ids:
            # Fetch Required Information
            video_data = video_cache[videoId]
            channel_data = channel_cache[channelID]

            # Fetch video snippet & content_details
            snippet = video_data[u"snippet"]
            content_details = video_data[u"contentDetails"]

            # Create listitem object
            item = listitem()

            # Add channel Fanart
            if channel_data["fanart"]:
                item.set_fanart(channel_data["fanart"])

            # Fetch video Image url
            item.set_thumb(snippet[u"thumbnails"][u"medium"][u"url"])

            # Fetch Title
            item.setLabel(snippet[u"localized"][u"title"])

            # Fetch Description
            item.info("plot", snippet[u"localized"][u"description"])

            # Fetch Studio
            item.info("studio", snippet[u"channelTitle"])

            # Fetch Possible Date
            date = snippet[u"publishedAt"]
            item.set_date(date[:date.find("T")], "%Y-%m-%d")

            # Fetch Viewcount
            item.info("count", video_data[u"statistics"][u"viewCount"])

            # Fetch Category
            cat_id = snippet[u"categoryId"]
            if cat_id in category_cache:
                item.info("genre", category_cache[cat_id])

            # Set Quality and Audio Overlays
            if is_hd >= 1 and content_details[u"definition"] == u"hd":
                item.addStreamInfo(is_hd)
            else:
                item.addStreamInfo(0)

            # Fetch Duration
            duration_str = content_details[u"duration"]
            duration_str = re_find("(\d+)(\w)", duration_str)
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
                item.set_duration(duration)

            # Add Context item to link to related videos
            item.menu_related(YTRelated, videoid=videoId, updatelisting=is_related)
            if len(channel_ids) > 1:
                item.menu_update(YTPlaylist, "Go to: %s" % snippet[u"channelTitle"], contentID=channelID)

            # Add InfoLabels and Data to Processed List
            yield item.get_direct(u"plugin://plugin.video.youtube/play/?video_id=%s" % video_data[u"id"])

        # Add next Page entry if pagetoken is giving
        if pagetoken:
            params = self.base.copy()
            params["pagetoken"] = pagetoken
            yield self.base.listitem.add_next(params)

        # Add playlists item to results
        if len(channel_ids) == 1 and u"pagetoken" not in self.base and self.base.get(u"enable_playlists", u"false")\
                == u"true":
            item = listitem()
            item.setLabel(u"[B]%s[/B]" % self.base.get_local_string("playlists"))
            item.set_icon("DefaultVideoPlaylists.png")
            item.set_thumb(u"youtube.png", 2)
            item["channelid"] = list(channel_ids)[0]
            yield item.get(YTPlaylists)


class API(object):
    """
    API class to handle requests to the youtube v3 api

    req_session : object --- Requests session object to handle the api requests
    """

    def __init__(self, req_session, lang="en", max_results="50", pretty_print="false",
                 key="AIzaSyCR4bRcTluwteqwplIC34wEf0GWi9PbSXQ"):
        # Setup Instance vars
        self.language = lang
        self.req_session = req_session
        self.default_params = {"maxResults": max_results, "prettyPrint": pretty_print, "key": key}

    def _connect_v3(self, api_type, params, max_age=None):
        """
        Send API request and return response as a json object

        api_type : string or unicode --- Type of API resource to fetch
        params : dict --- The parameters to use in the request
        """

        # Check api_type of video id(s) before making request
        if "id" in params and (isinstance(params["id"], list) or isinstance(params["id"], set)):
            params["id"] = u",".join(params["id"])

        url = "https://www.googleapis.com/youtube/v3/%s" % api_type
        source = self.req_session.get(url, params=params, headers={"X-Max-Age": max_age} if max_age else None)
        response = json.loads(source.content, encoding=None)  # encoding=source.encoding)
        if u"error" not in response:
            return response
        else:
            try:
                message = response[u"error"]["errors"][0][u"message"]
            except:
                raise RuntimeError("Youtube V3 API return and error response")
            else:
                raise RuntimeError("Youtube V3 API return and error response: %s" % message)

    def channels(self, channel_id=None, for_username=None):
        """
        Return all available information for giving channel

        channel_id : list or string or unicode --- ID of the channel for requesting infomation for.
        for_username : string or unicode --- Username of the channel for requesting information for.

        NOTE:
        Argument must be either channel_id or for_username but not both.
        If both are giving then channel_id will be used over for_username.
        """

        # Set parameters
        params = self.default_params.copy()
        params["fields"] = \
            u"items(id,brandingSettings/image/bannerTvMediumImageUrl,\
            contentDetails/relatedPlaylists/uploads,snippet/localized)"
        params["part"] = u"contentDetails,brandingSettings,snippet"
        params["hl"] = self.language

        # Add the channel_id or channel name of the channel to params
        if channel_id:
            params["id"] = channel_id
        elif for_username:
            params["forUsername"] = for_username
        else:
            raise ValueError("No valid Argument was giving for channels")

        # Connect to server and return json response
        return self._connect_v3("channels", params)

    def video_categories(self, cat_id=None, region_code="us"):
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
        params["regionCode"] = region_code

        # Set mode of fetching, by id or region
        if cat_id:
            params["id"] = cat_id

        # Fetch video Information
        return self._connect_v3("videoCategories", params)

    def playlist_items(self, playlist_id, pagetoken=None):
        """
        Return all videos ids for giving playlist ID

        playlist_id : string or unicode --- ID of Youtube playlist
        pagetoken : string or unicode --- The token for the next page of results
        """

        # Set parameters
        params = self.default_params.copy()
        params["fields"] = u"nextPageToken,items(snippet(channelId,resourceId/videoId),status/privacyStatus)"
        params["part"] = u"snippet,status"
        params["playlistId"] = playlist_id

        # Add pageToken if exists
        if pagetoken:
            params["pageToken"] = pagetoken

        # Connect to server and return json response
        return self._connect_v3("playlistItems", params)

    def videos(self, video_id):
        """
        Return all available information for giving video/vidoes

        video_id : list or string or unicode --- Video video_id(s) to fetch infomation for
        """

        # Set parameters
        params = self.default_params.copy()
        params["fields"] = u"items(video_id,snippet(publishedAt,channelId,thumbnails/medium/url,channelTitle,\
                            categoryId,localized),contentDetails(duration,definition),statistics/viewCount)"
        params["part"] = u"contentDetails,statistics,snippet"
        params["hl"] = self.language
        params["id"] = video_id

        # Connect to server and return json response
        return self._connect_v3("videos", params)

    def playlists(self, channel_id):
        """
        Return all playlist for a giving channel_id

        channel_id : string or unicode --- Id of the channel to fetch playlists for
        """

        # Set Default parameters
        params = self.default_params.copy()
        params["fields"] = u"nextPageToken,items(id,contentDetails/itemCount,snippet\
                            (publishedAt,localized,thumbnails/medium/url))"
        params["part"] = u"snippet,contentDetails"
        params["channelId"] = channel_id

        # Connect to server and return json response
        feed = self._connect_v3("playlists", params, 60 * 8)
        pagetoken = feed.get(u"nextPageToken")

        # Loop all pages
        while pagetoken:
            params["pageToken"] = pagetoken
            next_feed = self._connect_v3("playlists", params)
            feed[u"items"].extend(next_feed[u"items"])
            pagetoken = next_feed.get(u"nextPageToken")

        # Return all playlists
        feed[u"nextPageToken"] = None
        return feed

    def search(self, pagetoken=None, **search_params):
        """
        Return any search results

        pagetoken : string or unicode --- The token for the next page of results
        [search_params] : dict --- Youtube Data API search Parameters, refer to
                                   "https://developers.google.com/youtube/v3/docs/search/"
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
        if pagetoken:
            params["pageToken"] = pagetoken

        # Connect to server and return json response
        return self._connect_v3("search", params)
