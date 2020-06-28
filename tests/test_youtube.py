import unittest
import sqlite3
import inspect
import xbmc
import os

from codequick import youtube
from codequick.support import dispatcher


def clean_cache():
    """Remvoe the youtube cache file"""
    if os.path.exists(youtube.CACHEFILE):
        os.remove(youtube.CACHEFILE)


def route_caller(callback, *args, **kwargs):
    dispatcher.selector = callback.route.path
    try:
        results = callback.test(*args, **kwargs)
        if inspect.isgenerator(results):
            return list(results)
        else:
            return results
    finally:
        dispatcher.reset()


# noinspection PyTypeChecker
class Testcallbacks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clean_cache()

    def test_playlist_uploads_no_cache(self):
        ret = route_caller(youtube.playlist, "UCaWd5_7JhbQBe4dknZhsHJg")
        self.assertGreaterEqual(len(ret), 50)

    def test_playlist_uploads_with_cache(self):
        ret = route_caller(youtube.playlist, "UCaWd5_7JhbQBe4dknZhsHJg")
        self.assertGreaterEqual(len(ret), 50)

    def test_playlist_playlist_single_page(self):
        ret = route_caller(youtube.playlist, "PLmZTDWJGfRq3dT8teArT8RGg-SPpXErHK")
        self.assertGreaterEqual(len(ret), 10)

    def test_playlist_unlisted(self):
        ret = route_caller(youtube.playlist, "PLh6dr2Pr1VQnPdF29tkfQPgCBJPFnKYEV")
        self.assertGreaterEqual(len(ret), 17)

    def test_playlist_playlist_muilti_page(self):
        ret = route_caller(youtube.playlist, "PL8mG-RkN2uTx1lbFS8z8wRYS3RrHCp8TG", loop=False)
        self.assertGreaterEqual(len(ret), 49)

    def test_playlist_playlist_loop(self):
        ret = route_caller(youtube.playlist, "PL8mG-RkN2uTx1lbFS8z8wRYS3RrHCp8TG", loop=True)
        self.assertGreaterEqual(len(ret), 66)

    def test_related(self):
        ret = route_caller(youtube.related, "-QEXPO9zgX8")
        self.assertGreaterEqual(len(ret), 50)

    def test_playlists(self):
        ret = route_caller(youtube.playlists, "UCaWd5_7JhbQBe4dknZhsHJg")
        self.assertGreaterEqual(len(ret), 50)

    def test_playlists_with_uploade_id(self):
        with self.assertRaises(ValueError):
            route_caller(youtube.playlists, "UUewxof_QqDdqVdXY1BaDtqQ")

    def test_playlists_disable_all_link(self):
        ret = route_caller(youtube.playlists, "UCaWd5_7JhbQBe4dknZhsHJg", show_all=False)
        self.assertGreaterEqual(len(ret), 50)

    def test_bad_channel_id(self):
        with self.assertRaises(KeyError):
            route_caller(youtube.playlist, "UCad5_7JhQBe4dknZhsJg")


class TestAPIControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clean_cache()

    def setUp(self):
        self.api = youtube.APIControl()

    def tearDown(self):
        try:
            self.api.close()
        except sqlite3.ProgrammingError:
            pass
        self.api = None
        dispatcher.reset()

    def test_valid_playlistid(self):
        ret = self.api.valid_playlistid("UCaWd5_7JhbQBe4dknZhsHJg")
        self.assertEqual(ret, "UUaWd5_7JhbQBe4dknZhsHJg")

    def test_valid_playlistid_unknown(self):
        with self.assertRaises(KeyError):
            self.api.valid_playlistid("UCad5_7JhQBe4dknZhsJg")

    def test_valid_playlistid_invalid(self):
        with self.assertRaises(ValueError):
            self.api.valid_playlistid("-QEXPO9zgX8")

    def test_convert_duration_seconds(self):
        test_match = [(u'42', u'S')]
        ret = self.api._convert_duration(test_match)
        self.assertEqual(ret, 42)

    def test_convert_duration_minutes(self):
        test_match = [(u'11', u'M'), (u'42', u'S')]
        ret = self.api._convert_duration(test_match)
        self.assertEqual(ret, 702)

    def test_convert_duration_hours(self):
        test_match = [(u'1', u'H'), (u'11', u'M'), (u'42', u'S')]
        ret = self.api._convert_duration(test_match)
        self.assertEqual(ret, 4302)


class TestDB(unittest.TestCase):
    def setUp(self):
        self.db = youtube.Database()

    def tearDown(self):
        try:
            self.db.close()
        except sqlite3.ProgrammingError:
            pass
        self.db = None
        dispatcher.reset()

    def test_close(self):
        self.db.close()

    def test_cleanup_no_run(self):
        self.db.cleanup()

    def test_cleanup_run(self):
        org_cur = self.db.cur

        class Cur(object):
            @staticmethod
            def execute(_):
                class Fetchone(object):
                    @staticmethod
                    def fetchone():
                        return [15000]

                self.db.cur = org_cur
                return Fetchone()

        self.db.cur = Cur()

        try:
            self.db.cleanup()
        finally:
            self.db.cur = org_cur
