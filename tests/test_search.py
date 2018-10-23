from addondev import testing
import unittest
import xbmc
import os

# Testing specific imports
from codequick import search, route, storage
from codequick.support import dispatcher
from codequick.listing import Listitem
from codequick.search import hash_params


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
        path = os.path.join(storage.profile_dir, search.SEARCH_DB)
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
            yield Listitem.from_dict(results, "listitem one")
            yield Listitem.from_dict(results, "listitem two")

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(first_load=True, execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertIn("Rock", db[session_id])

        self.assertEqual(len(listitems), 2)
        self.assertEqual(listitems[0].label, "listitem one")
        self.assertEqual(listitems[1].label, "listitem two")

    def test_first_load_invalid(self):
        @route.Route.register
        def results(_, search_query):
            self.assertEqual(search_query, "Rock")
            return False

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(first_load=True, execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertNotIn("Rock", db[session_id])

        self.assertFalse(listitems)

    def test_first_load_canceled(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with testing.mock_keyboard(""):
            listitems = search.SavedSearches.test(first_load=True, execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertFalse(bool(db[session_id]))

        self.assertFalse(listitems)

    def test_search_empty(self):
        @route.Route.register
        def results(_, search_query):
            self.assertEqual(search_query, "Rock")
            yield Listitem.from_dict(results, "listitem one")
            yield Listitem.from_dict(results, "listitem two")

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(search=True, execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertIn("Rock", db[session_id])

        self.assertEqual(len(listitems), 2)
        self.assertEqual(listitems[0].label, "listitem one")
        self.assertEqual(listitems[1].label, "listitem two")

    def test_search_populated(self):
        @route.Route.register
        def results(_, search_query):
            self.assertEqual(search_query, "Rock")
            yield Listitem.from_dict(results, "listitem one")
            yield Listitem.from_dict(results, "listitem two")

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            dbstore = db.setdefault(session_id, [])
            dbstore.append("Pop")
            db.flush()

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(search=True, execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertIn("Rock", db[session_id])
            self.assertIn("Pop", db[session_id])

        self.assertEqual(len(listitems), 2)
        self.assertEqual(listitems[0].label, "listitem one")
        self.assertEqual(listitems[1].label, "listitem two")

    def test_search_populated_invalid(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            dbstore = db.setdefault(session_id, [])
            dbstore.append("Pop")
            db.flush()

        with testing.mock_keyboard(""):
            listitems = search.SavedSearches.test(search=True, execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertIn("Pop", db[session_id])

        self.assertEqual(len(listitems), 2)
        self.assertIn("Search", listitems[0].label)
        self.assertEqual(listitems[1].label, "Pop")

    def test_saved_firstload(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            dbstore = db.setdefault(session_id, [])
            dbstore.append("Rock")
            dbstore.append("Pop")
            db.flush()

        listitems = search.SavedSearches.test(first_load=True, execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertIn("Rock", db[session_id])
            self.assertIn("Pop", db[session_id])

        self.assertEqual(len(listitems), 3)
        self.assertIn("Search", listitems[0].label)
        self.assertEqual(listitems[1].label, "Rock")
        self.assertEqual(listitems[2].label, "Pop")

    def test_saved_sessions(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def session_one(_, search_query):
            self.assertEqual(search_query, "Rock")
            yield Listitem.from_dict(session_one, "listitem one")
            yield Listitem.from_dict(session_one, "listitem two")

        # noinspection PyUnusedLocal
        @route.Route.register
        def session_two(_, search_query):
            self.assertEqual(search_query, "Pop")
            yield Listitem.from_dict(session_two, "listitem one")
            yield Listitem.from_dict(session_two, "listitem two")

        session_one_params = dict(_route=session_one.route.path)
        session_one_id = hash_params(session_one_params)

        session_two_params = dict(_route=session_two.route.path)
        session_two_id = hash_params(session_two_params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            dbstore = db.setdefault(session_one_id, [])
            dbstore.append("Jazz")
            dbstore = db.setdefault(session_two_id, [])
            dbstore.append("Chill")
            db.flush()

        with testing.mock_keyboard("Rock"):
            search.SavedSearches.test(search=True, execute_delayed=True, **session_one_params)

        with testing.mock_keyboard("Pop"):
            search.SavedSearches.test(search=True, execute_delayed=True, **session_two_params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_one_id, db)
            self.assertIn("Rock", db[session_one_id])
            self.assertNotIn("Pop", db[session_one_id])

            self.assertIn(session_two_id, db)
            self.assertIn("Pop", db[session_two_id])
            self.assertNotIn("Rock", db[session_two_id])

    def test_saved_not_firstload(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            dbstore = db.setdefault(session_id, [])
            dbstore.append("Rock")
            dbstore.append("Pop")
            db.flush()

        with testing.mock_keyboard("Rock"):
            listitems = search.SavedSearches.test(execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertIn("Rock", db[session_id])
            self.assertIn("Pop", db[session_id])

        self.assertEqual(len(listitems), 3)
        self.assertIn("Search", listitems[0].label)
        self.assertEqual(listitems[1].label, "Rock")
        self.assertEqual(listitems[2].label, "Pop")

    def test_saved_remove(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def results(_, search_query):
            pass

        params = dict(_route=results.route.path)
        session_id = hash_params(params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            dbstore = db.setdefault(session_id, [])
            dbstore.append("Rock")
            dbstore.append("Pop")
            db.flush()

        listitems = search.SavedSearches.test(remove_entry="Rock", execute_delayed=True, **params)

        with storage.PersistentDict(search.SEARCH_DB) as db:
            self.assertIn(session_id, db)
            self.assertNotIn("Rock", db[session_id])
            self.assertIn("Pop", db[session_id])

        self.assertEqual(len(listitems), 2)
        self.assertIn("Search", listitems[0].label)
        self.assertEqual(listitems[1].label, "Pop")
