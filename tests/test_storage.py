import unittest
import shutil
import os

# Testing specific imports
from codequick import storage


class StorageDict(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(StorageDict, self).__init__(*args, **kwargs)
        self.filename = "dictfile.pickle"

    def setUp(self):
        path = os.path.join(storage.profile_dir, self.filename)
        if os.path.exists(path):
            os.remove(path)

    def test_create_filename(self):
        """Should not fail"""
        with storage.PersistentDict(self.filename) as db:
            self.assertFalse(db)
            self.assertIsNone(db._stream)

    def test_create_filepath(self):
        """Should not fail"""
        path = os.path.join(storage.profile_dir, self.filename)
        with storage.PersistentDict(path) as db:
            self.assertFalse(db)
            self.assertIsNone(db._stream)

    def test_flush(self):
        with storage.PersistentDict(self.filename) as db:
            db["test"] = "data"
            db.flush()
            self.assertIn("test", db)

    def test_flush_with_missing_dir(self):
        shutil.rmtree(storage.profile_dir)
        with storage.PersistentDict(self.filename) as db:
            db["test"] = "data"
            db.flush()
            self.assertIn("test", db)

    def test_persistents(self):
        with storage.PersistentDict(self.filename) as db:
            db["persistent"] = "true"
            db.flush()
            self.assertIn("persistent", db)

        with storage.PersistentDict(self.filename) as db:
            self.assertIn("persistent", db)
            self.assertEqual(db["persistent"], "true")


class StorageList(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(StorageList, self).__init__(*args, **kwargs)
        self.filename = "listfile.pickle"

    def setUp(self):
        path = os.path.join(storage.profile_dir, self.filename)
        if os.path.exists(path):
            os.remove(path)

    def test_create_filename(self):
        """Should not fail"""
        with storage.PersistentList(self.filename) as db:
            self.assertFalse(db)
            self.assertIsNone(db._stream)

    def test_create_filepath(self):
        """Should not fail"""
        path = os.path.join(storage.profile_dir, self.filename)
        with storage.PersistentList(path) as db:
            self.assertFalse(db)
            self.assertIsNone(db._stream)

    def test_flush(self):
        with storage.PersistentList(self.filename) as db:
            db.append("data")
            db.flush()
            self.assertIn("data", db)

    def test_flush_with_missing_dir(self):
        shutil.rmtree(storage.profile_dir)
        with storage.PersistentList(self.filename) as db:
            db.append("data")
            db.flush()
            self.assertIn("data", db)

    def test_reflush(self):
        with storage.PersistentList(self.filename) as db:
            db.append("persistent")
            db.flush()
            db.flush()

    def test_persistents(self):
        with storage.PersistentList(self.filename) as db:
            db.append("persistent")
            db.flush()
            self.assertIn("persistent", db)

        with storage.PersistentList(self.filename) as db:
            db.append("persistent2")
            self.assertIn("persistent", db)
            self.assertIn("persistent2", db)
            db.flush()
