import unittest
from addondev.testing import plugin_data
import xbmc

from codequick.listing import Listitem
from codequick.support import auto_sort
from codequick import route


@route.Route.register
def callback_test(_):
    pass


class TestGlobalLocalization(unittest.TestCase):
    def test_select_playback_item(self):
        ret = xbmc.getLocalizedString(route.SELECT_PLAYBACK_ITEM)
        self.assertEqual(ret, "Select playback item")

    def test_nodata(self):
        ret = xbmc.getLocalizedString(route.NO_DATA)
        self.assertEqual(ret, "No data found!")


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.route = route.Route()

    def test_gen(self):
        def route_gen():
            yield Listitem.from_dict(callback_test, "test item")

        self.route._process_results(route_gen())
        self.assertTrue(plugin_data["succeeded"])

    def test_list(self):
        self.route._process_results([Listitem.from_dict(callback_test, "test item")])
        self.assertTrue(plugin_data["succeeded"])

    def test_return_false(self):
        self.route._process_results(False)
        self.assertFalse(plugin_data["succeeded"])

    def test_yield_false(self):
        def route_list():
            yield False

        self.route._process_results(route_list())
        self.assertFalse(plugin_data["succeeded"])

    def test_no_items(self):
        with self.assertRaises(RuntimeError):
            self.route._process_results([])

    def test_one_mediatype(self):
        def route_list():
            yield Listitem.from_dict(callback_test, "test item", info={"mediatype": "video"})

        self.route._process_results(route_list())
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["contenttype"], "videos")

    def test_two_mediatype(self):
        def route_list():
            yield Listitem.from_dict(callback_test, "test item one", info={"mediatype": "video"})
            yield Listitem.from_dict(callback_test, "test item two", info={"mediatype": "movie"})
            yield Listitem.from_dict(callback_test, "test item three", info={"mediatype": "video"})

        self.route._process_results(route_list())
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["contenttype"], "videos")

    def test_unsupported_mediatype(self):
        def route_list():
            yield Listitem.from_dict(callback_test, "season one", info={"mediatype": "season"})

        self.route._process_results(route_list())
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["contenttype"], "files")

    def test_sortmethod(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list():
            yield Listitem.from_dict("season one", "test.mkv")

        self.route._process_results(route_list())
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [10])

    def test_sortmethod_genre(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list():
            yield Listitem.from_dict("season one", "test.mkv", info={"genre": "test"})

        self.route._process_results(route_list())
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [10, 16])

    def test_no_sort(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(plugin):
            plugin.autosort = False
            yield Listitem.from_dict("season one", "test.mkv")

        self.route._process_results(route_list(self.route))
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [40])

    def test_no_sort_genre(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(plugin):
            plugin.autosort = False
            yield Listitem.from_dict("season one", "test.mkv", info={"genre": "test"})

        self.route._process_results(route_list(self.route))
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [40])

    def test_custom_sort_only(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(plugin):
            plugin.autosort = False
            plugin.add_sort_methods(3)
            yield Listitem.from_dict("season one", "test.mkv", info={"genre": "test"})

        self.route._process_results(route_list(self.route))
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [3])

    def test_custom_sort_with_autosort(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(plugin):
            plugin.add_sort_methods(3)
            yield Listitem.from_dict("season one", "test.mkv", info={"genre": "test"})

        self.route._process_results(route_list(self.route))
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [3, 10, 16])
