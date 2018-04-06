import unittest
import urlquick
import sys

from addondev.testing import plugin_data, mock_select_dialog
from xbmcgui import ListItem as kodi_listitem
import xbmc

from codequick import resolver
from codequick.listing import Listitem as custom_listitem
from codequick.support import dispatcher

from . import YDStreamExtractor
sys.modules["YDStreamExtractor"] = YDStreamExtractor


def temp_callback(func):
    def wrapper(*args):
        # noinspection PyUnusedLocal
        @resolver.Resolver.register
        def root(_):
            pass

        try:
            func(*args)
        finally:
            del dispatcher.registered_routes[root.route.path]

    return wrapper


class TestGlobalLocalization(unittest.TestCase):
    def test_select_playback_item(self):
        ret = xbmc.getLocalizedString(resolver.SELECT_PLAYBACK_ITEM)
        self.assertEqual(ret, "Select playback item")

    def test_nodata(self):
        ret = xbmc.getLocalizedString(resolver.NO_DATA)
        self.assertEqual(ret, "No data found!")


class TestResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = resolver.Resolver()

    def test_bytes(self):
        self.resolver._process_results(b"test.mkv")
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_unicode(self):
        self.resolver._process_results(u"test.mkv")
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_no_url(self):
        with self.assertRaises(ValueError):
            self.resolver._process_results(None)

    def test_invalid_url(self):
        with self.assertRaises(ValueError):
            self.resolver._process_results(9)

    def test_kodi_listitem(self):
        item = kodi_listitem()
        item.setLabel("test")
        item.setPath(u"test.mkv")

        self.resolver._process_results(item)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_custom_listitem(self):
        item = custom_listitem()
        item.label = "test"
        item.set_callback(u"test.mkv")

        self.resolver._process_results(item)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_list(self):
        del plugin_data["playlist"][:]

        self.resolver._process_results([u"test.mkv", u"tester.mkv"])
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 2)

    def test_tuple(self):
        del plugin_data["playlist"][:]

        self.resolver._process_results((u"test.mkv", u"tester.mkv"))
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 2)

    def test_dict(self):
        del plugin_data["playlist"][:]

        self.resolver._process_results({"test": "test.mkv"})
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 1)

    def test_gen_single(self):
        del plugin_data["playlist"][:]

        def eg_resolver():
            yield "test_one.mkv"

        self.resolver._process_results(eg_resolver())
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test_one.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 1)

    def test_gen_multi(self):
        del plugin_data["playlist"][:]

        def eg_resolver():
            yield "test_one.mkv"
            yield "test_two.mkv"

        self.resolver._process_results(eg_resolver())
        dispatcher.run_metacalls()
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test_one.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 2)

    def test_playlist_kodi_listitem(self):
        del plugin_data["playlist"][:]

        item = kodi_listitem()
        item.setLabel("test")
        item.setPath(u"test.mkv")

        self.resolver._process_results([item])
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_playlist_custom_listitem(self):
        del plugin_data["playlist"][:]

        item = custom_listitem()
        item.label = "test"
        item.set_callback(u"test.mkv")

        self.resolver._process_results([item])
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    @temp_callback
    def test_create_loopback(self):
        del plugin_data["playlist"][:]

        self.resolver.create_loopback("video.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 2)

    @temp_callback
    def test_continue_loopback(self):
        del plugin_data["playlist"][:]
        self.resolver._title = "_loopback_ - tester"

        self.resolver.create_loopback("video.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 1)

    def test_extract_source(self):
        YDStreamExtractor.mode = 0  # single
        ret = self.resolver.extract_source("url")
        self.assertEqual(ret, "video.mkv")

    def test_extract_novideo(self):
        YDStreamExtractor.mode = 2  # novideo
        ret = self.resolver.extract_source("url")
        self.assertIsNone(ret)

    def test_extract_sourcewith_params(self):
        YDStreamExtractor.mode = 0  # novideo
        ret = self.resolver.extract_source("url", novalidate=True)
        self.assertEqual(ret, "video.mkv")

    def test_extract_source_multiple(self):
        YDStreamExtractor.mode = 1  # multiple
        with mock_select_dialog(0):
            ret = self.resolver.extract_source("url")
        self.assertEqual(ret, "video.mkv")

    def test_extract_source_multiple_canceled(self):
        YDStreamExtractor.mode = 1  # multiple
        with mock_select_dialog(-1):
            ret = self.resolver.extract_source("url")
        self.assertIsNone(ret)

    def test_extract_source_error(self):
        YDStreamExtractor.mode = 3  # raise error
        with self.assertRaises(RuntimeError):
            self.resolver.extract_source("url")

    def test_extract_source_warning(self):
        YDStreamExtractor.mode = 4  # raise warning
        ret = self.resolver.extract_source("url")
        self.assertEqual(ret, "video.mkv")

    def test_extract_youtube_url(self):
        ret = self.resolver.extract_youtube("https://www.watchmojo.com/video/id/20838/")
        self.assertEqual(ret, "plugin://plugin.video.youtube/play/?video_id=P3PvFiCibts")

    def test_extract_youtube_source(self):
        source = urlquick.get("https://www.watchmojo.com/video/id/20838/").text
        ret = self.resolver.extract_youtube(source)
        self.assertEqual(ret, "plugin://plugin.video.youtube/play/?video_id=P3PvFiCibts")

    def test_extract_youtube_node(self):
        html = urlquick.get("https://www.watchmojo.com/video/id/20838/")
        video_elem = html.parse("div", attrs={"id": "question"})
        ret = self.resolver.extract_youtube(video_elem)
        self.assertEqual(ret, "plugin://plugin.video.youtube/play/?video_id=P3PvFiCibts")

    def test_extract_youtube_no_video(self):
        ret = self.resolver.extract_youtube("https://www.youtube.com/")
        self.assertIsNone(ret)
