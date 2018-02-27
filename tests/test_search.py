from addondev import testing
import unittest
import xbmc
import os

# Testing specific imports
from codequick import search, route, storage
from codequick.support import dispatcher
from codequick.listing import Listitem


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

    def test_first_load(self):
        @route.Route.register
        def results(_, search_query):
            self.assertEqual(search_query, "Rock")
            yield Listitem.from_dict("listitem one", results)
            yield Listitem.from_dict("listitem two", results)

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(first_load=True, route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertIn("Rock", db)

        self.assertEqual(len(listitems), 2)
        self.assertEqual(listitems[0].label, "listitem one")
        self.assertEqual(listitems[1].label, "listitem two")

    def test_first_load_invalid(self):
        @route.Route.register
        def results(_, search_query):
            self.assertEqual(search_query, "Rock")
            return False

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(first_load=True, route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertNotIn("Rock", db)

        self.assertFalse(listitems)

    def test_first_load_canceled(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        with testing.mock_keyboard(""):
            listitems = search.SavedSearches.test(first_load=True, route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertFalse(bool(db))

        self.assertFalse(listitems)

    def test_search_empty(self):
        @route.Route.register
        def results(_, search_query):
            self.assertEqual(search_query, "Rock")
            yield Listitem.from_dict("listitem one", results)
            yield Listitem.from_dict("listitem two", results)

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(search=True, route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertIn("Rock", db)

        self.assertEqual(len(listitems), 2)
        self.assertEqual(listitems[0].label, "listitem one")
        self.assertEqual(listitems[1].label, "listitem two")

    def test_search_populated(self):
        @route.Route.register
        def results(_, search_query):
            self.assertEqual(search_query, "Rock")
            yield Listitem.from_dict("listitem one", results)
            yield Listitem.from_dict("listitem two", results)

        with storage.PersistentList(search.SEARCH_DB) as db:
            db.append("Pop")
            db.flush()

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(search=True, route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertIn("Rock", db)
            self.assertIn("Pop", db)

        self.assertEqual(len(listitems), 2)
        self.assertEqual(listitems[0].label, "listitem one")
        self.assertEqual(listitems[1].label, "listitem two")

    def test_search_populated_invalid(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        with storage.PersistentList(search.SEARCH_DB) as db:
            db.append("Pop")
            db.flush()

        with testing.mock_keyboard(""):
            listitems = search.SavedSearches.test(search=True, route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertIn("Pop", db)

        self.assertEqual(len(listitems), 2)
        self.assertIn("Search", listitems[0].label)
        self.assertEqual(listitems[1].label, "Pop")

    def test_saved_firstload(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        with storage.PersistentList(search.SEARCH_DB) as db:
            db.append("Rock")
            db.append("Pop")
            db.flush()

        listitems = search.SavedSearches.test(first_load=True, route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertIn("Rock", db)
            self.assertIn("Pop", db)

        self.assertEqual(len(listitems), 3)
        self.assertIn("Search", listitems[0].label)
        self.assertEqual(listitems[1].label, "Rock")
        self.assertEqual(listitems[2].label, "Pop")

    def test_saved_not_firstload(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        with storage.PersistentList(search.SEARCH_DB) as db:
            db.append("Rock")
            db.append("Pop")
            db.flush()

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertIn("Rock", db)
            self.assertIn("Pop", db)

        self.assertEqual(len(listitems), 3)
        self.assertIn("Search", listitems[0].label)
        self.assertEqual(listitems[1].label, "Rock")
        self.assertEqual(listitems[2].label, "Pop")

    def test_saved_remove(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        with storage.PersistentList(search.SEARCH_DB) as db:
            db.append("Rock")
            db.append("Pop")
            db.flush()

        listitems = search.SavedSearches.test(remove_entry="Rock", route=results.route.path, execute_delayed=True)

        with storage.PersistentList(search.SEARCH_DB) as db:
            self.assertNotIn("Rock", db)
            self.assertIn("Pop", db)

        self.assertEqual(len(listitems), 2)
        self.assertIn("Search", listitems[0].label)
        self.assertEqual(listitems[1].label, "Pop")
