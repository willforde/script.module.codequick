import unittest
import os

from codequick import youtube


def clean_cache():
    """Remvoe the youtube cache file"""
    if os.path.exists(youtube.CACHEFILE):
        os.remove(youtube.CACHEFILE)


class Testcallbacks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clean_cache()

    def test_playlist_uploads_no_cache(self):
        clean_cache()
        ret = youtube.Playlist.test("UCaWd5_7JhbQBe4dknZhsHJg")
        self.assertGreaterEqual(len(ret), 50)

    def test_playlist_uploads_with_cache(self):
        ret = youtube.Playlist.test("UCaWd5_7JhbQBe4dknZhsHJg")
        self.assertGreaterEqual(len(ret), 50)

    def test_playlist_playlist_single_page(self):
        ret = youtube.Playlist.test("PLmZTDWJGfRq3dT8teArT8RGg-SPpXErHK")
        self.assertGreaterEqual(len(ret), 10)

    def test_playlist_playlist_muilti_page(self):
        ret = youtube.Playlist.test("PLmZTDWJGfRq0SPaFDyvl9c_vS3NbhQweH", loop=False)
        self.assertGreaterEqual(len(ret), 50)

    def test_playlist_playlist_loop(self):
        ret = youtube.Playlist.test("PLmZTDWJGfRq0SPaFDyvl9c_vS3NbhQweH", loop=True)
        self.assertGreaterEqual(len(ret), 80)

    def test_related(self):
        ret = youtube.Related.test("-QEXPO9zgX8")
        self.assertGreaterEqual(len(ret), 50)

    def test_playlists(self):
        ret = youtube.Playlists.test("UCaWd5_7JhbQBe4dknZhsHJg")
        self.assertGreaterEqual(len(ret), 50)

    def test_playlists_with_uploade_id(self):
        with self.assertRaises(ValueError):
            youtube.Playlists.test("UUewxof_QqDdqVdXY1BaDtqQ")

    def test_playlists_disable_all_link(self):
        ret = youtube.Playlists.test("UCaWd5_7JhbQBe4dknZhsHJg", show_all=False)
        self.assertGreaterEqual(len(ret), 50)

    def test_playvideo(self):
        ret = youtube.play_video.test("-QEXPO9zgX8")
        self.assertEqual(ret, "plugin://plugin.video.youtube/play/?video_id=-QEXPO9zgX8")


class TestAPIControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clean_cache()

    def setUp(self):
        self.api = youtube.APIControl()

    def tearDown(self):
        self.api = None

    def test_valid_playlistid(self):
        with self.assertRaises(ValueError):
            self.api.valid_playlistid("-QEXPO9zgX8")
