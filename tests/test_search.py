from addondev import testing
import unittest
import xbmc
import os

# Testing specific imports
from codequick import search, route, storage
from codequick.support import dispatcher


class TestGlobalLocalization(unittest.TestCase):
    def test_enter_search_string(self):
        ret = xbmc.getLocalizedString(search.ENTER_SEARCH_STRING)
        self.assertEqual(ret, "Enter search string")

    def test_remove(self):
        ret = xbmc.getLocalizedString(search.REMOVE)
        self.assertEqual(ret, "Remove")

    def test_search(self):
        ret = xbmc.getLocalizedString(search.SEARCH)
        self.assertEqual(ret, "Search")


class Search(unittest.TestCase):
    def setUp(self):
        self.org_routes = dispatcher.registered_routes.copy()
        path = os.path.join(storage.profile_dir, u"_searches.pickle")
        if os.path.exists(path):
            os.remove(path)

    def tearDown(self):
        dispatcher.reset()
        dispatcher.registered_routes.clear()
        dispatcher.registered_routes.update(self.org_routes)

    def test_first_run(self):
        @route.Route.register
        def search_results(_):
            pass

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(route=search_results.route.path)

        self.assertEqual(len(listitems), 2)
        self.assertEqual(listitems[-1].label, "Rock")

    def test_force_search(self):
        @route.Route.register
        def search_results(_):
            pass

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(search=True, route=search_results.route.path)

        self.assertEqual(len(listitems), 2)
        self.assertEqual(listitems[-1].label, "Rock")

    def test_empty_search(self):
        @route.Route.register
        def search_results(_):
            pass

        with testing.mock_keyboard(""):
            listitems = search.SavedSearches.test(route=search_results.route.path)

        self.assertFalse(listitems)

    def test_remove(self):
        @route.Route.register
        def search_results(_):
            pass

        with storage.PersistentList(u"_searches.pickle") as db:
            db.append("Rock")
            db.flush()

        listitems = search.SavedSearches.test("Rock", route=search_results.route.path)
        self.assertEqual(len(listitems), 1)
        self.assertNotEqual(listitems[0].label, "rock")
