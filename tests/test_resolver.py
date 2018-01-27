import unittest
import sys

from addondev.testing import plugin_data, mock_select_dialog
from xbmcgui import ListItem as kodi_listitem

from codequick import resolver
from codequick.listing import Listitem as custom_listitem

from . import YDStreamExtractor
sys.modules["YDStreamExtractor"] = YDStreamExtractor


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.resolver = resolver.Resolver()

    def test_bytes(self):
        def eg_resolver(_):
            return b"test.mkv"

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_unicode(self):
        def eg_resolver(_):
            return u"test.mkv"

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_no_url(self):
        def eg_resolver(_):
            return None

        with self.assertRaises(ValueError):
            self.resolver._execute_route(eg_resolver)

    def test_invalid_url(self):
        def eg_resolver(_):
            return 9

        with self.assertRaises(ValueError):
            self.resolver._execute_route(eg_resolver)

    def test_kodi_listitem(self):
        def eg_resolver(_):
            item = kodi_listitem()
            item.setLabel("test")
            item.setPath(u"test.mkv")
            return item

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_custom_listitem(self):
        def eg_resolver(_):
            item = custom_listitem()
            item.label = "test"
            item.set_callback(u"test.mkv")
            return item

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_list(self):
        del plugin_data["playlist"][:]

        def eg_resolver(_):
            return [u"test.mkv", u"tester.mkv"]

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 2)

    def test_tuple(self):
        del plugin_data["playlist"][:]

        def eg_resolver(_):
            return u"test.mkv", u"tester.mkv"

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 2)

    def test_dict(self):
        del plugin_data["playlist"][:]

        def eg_resolver(_):
            return {"test": "test.mkv"}

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 1)

    def test_playlist_kodi_listitem(self):
        del plugin_data["playlist"][:]

        def eg_resolver(_):
            item = kodi_listitem()
            item.setLabel("test")
            item.setPath(u"test.mkv")
            return [item]

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_playlist_custom_listitem(self):
        del plugin_data["playlist"][:]

        def eg_resolver(_):
            item = custom_listitem()
            item.label = "test"
            item.set_callback(u"test.mkv")
            return [item]

        self.resolver._execute_route(eg_resolver)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["resolved"]["path"], u"test.mkv")

    def test_create_loopback(self):
        del plugin_data["playlist"][:]

        self.resolver.create_loopback("video.mkv")
        self.assertEqual(len(plugin_data["playlist"]), 2)

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
