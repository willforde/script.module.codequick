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
        def route_gen(_):
            yield Listitem.from_dict("test item", callback_test)

        self.route._execute_route(route_gen)
        self.assertTrue(plugin_data["succeeded"])

    def test_list(self):
        def route_list(_):
            return [Listitem.from_dict("test item", callback_test)]

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])

    def test_return_false(self):
        def route_list(_):
            return False

        self.route._execute_route(route_list)
        self.assertFalse(plugin_data["succeeded"])

    def test_yield_false(self):
        def route_list(_):
            yield False

        self.route._execute_route(route_list)
        self.assertFalse(plugin_data["succeeded"])

    def test_no_items(self):
        def route_list(_):
            return []

        with self.assertRaises(RuntimeError):
            self.route._execute_route(route_list)

    def test_one_mediatype(self):
        def route_list(_):
            yield Listitem.from_dict("test item", callback_test, info={"mediatype": "video"})

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["contenttype"], "videos")

    def test_two_mediatype(self):
        def route_list(_):
            yield Listitem.from_dict("test item one", callback_test, info={"mediatype": "video"})
            yield Listitem.from_dict("test item two", callback_test, info={"mediatype": "movie"})
            yield Listitem.from_dict("test item three", callback_test, info={"mediatype": "video"})

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["contenttype"], "videos")

    def test_unsupported_mediatype(self):
        def route_list(_):
            yield Listitem.from_dict("season one", callback_test, info={"mediatype": "season"})

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertEqual(plugin_data["contenttype"], "files")

    def test_sortmethod(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(_):
            yield Listitem.from_dict("season one", "test.mkv")

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [10])

    def test_sortmethod_genre(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(_):
            yield Listitem.from_dict("season one", "test.mkv", info={"genre": "test"})

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [10, 16])

    def test_no_sort(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(plugin):
            plugin.autosort = False
            yield Listitem.from_dict("season one", "test.mkv")

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [40])

    def test_no_sort_genre(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(plugin):
            plugin.autosort = False
            yield Listitem.from_dict("season one", "test.mkv", info={"genre": "test"})

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [40])

    def test_custom_sort_only(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(plugin):
            plugin.autosort = False
            plugin.add_sort_methods(3)
            yield Listitem.from_dict("season one", "test.mkv", info={"genre": "test"})

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [3])

    def test_custom_sort_with_autosort(self):
        auto_sort.clear()
        del plugin_data["sortmethods"][:]

        def route_list(plugin):
            plugin.add_sort_methods(3)
            yield Listitem.from_dict("season one", "test.mkv", info={"genre": "test"})

        self.route._execute_route(route_list)
        self.assertTrue(plugin_data["succeeded"])
        self.assertListEqual(plugin_data["sortmethods"], [3, 10, 16])
