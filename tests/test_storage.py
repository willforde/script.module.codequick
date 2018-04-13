import unittest
import shutil
import pickle
import time
import os

# Testing specific imports
from codequick import storage


class StorageDict(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(StorageDict, self).__init__(*args, **kwargs)
        self.filename = "dictfile.pickle"
        self.path = os.path.join(storage.profile_dir, self.filename)

    def setUp(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_create_filename_part(self):
        with storage.PersistentDict(self.filename) as db:
            self.assertFalse(db)
            self.assertIsNone(db._stream)

    def test_create_filename_full(self):
        with storage.PersistentDict(self.path) as db:
            self.assertFalse(db)
            self.assertIsNone(db._stream)

    def test_flush_with_data(self):
        with storage.PersistentDict(self.filename) as db:
            db["test"] = "data"
            db.flush()
            self.assertIn("test", db)

    def test_flush_no_data(self):
        with storage.PersistentDict(self.filename) as db:
            db.flush()

    def test_flush_with_missing_dir(self):
        shutil.rmtree(storage.profile_dir)
        with storage.PersistentDict(self.filename) as db:
            db["test"] = "data"
            db.flush()
            self.assertIn("test", db)

    def test_persistents(self):
        with storage.PersistentDict(self.filename) as db:
            db["persistent"] = "true"
            self.assertIn("persistent", db)

        with storage.PersistentDict(self.filename) as db:
            self.assertIn("persistent", db)
            self.assertEqual(db["persistent"], "true")

    def test_get(self):
        with storage.PersistentDict(self.filename) as db:
            db.update({"one": 1, "two": 2})
            self.assertEqual(db["two"], 2)

    def test_set(self):
        with storage.PersistentDict(self.filename) as db:
            db["one"] = 1
            self.assertIn("one", db)
            self.assertEqual(db["one"], 1)

    def test_del(self):
        with storage.PersistentDict(self.filename) as db:
            db.update({"one": 1, "two": 2})
            del db["one"]
            self.assertNotIn("one", db)
            self.assertIn("two", db)

    def test_len(self):
        with storage.PersistentDict(self.filename) as db:
            db.update({"one": 1, "two": 2})
            self.assertEqual(len(db), 2)

    def test_iter(self):
        with storage.PersistentDict(self.filename) as db:
            db.update({"one": 1, "two": 2})
            data = list(iter(db))
            self.assertEqual(len(data), 2)
            self.assertIn("one", data)
            self.assertIn("two", data)

    def test_items(self):
        with storage.PersistentDict(self.filename) as db:
            db.update({"one": 1, "two": 2})
            data = list(db.items())
            self.assertEqual(len(data), 2)
            expected = [("one", 1), ("two", 2)]
            for item in data:
                self.assertIn(item, expected)

    def test_version_convert(self):
        with open(self.path, "wb") as db:
            pickle.dump({"one": 1, "two": 2}, db, protocol=2)

        with storage.PersistentDict(self.filename) as db:
            self.assertIn("one", db)
            self.assertIn("two", db)

    def test_ttl(self):
        with open(self.path, "wb") as db:
            pickle.dump({"one": 1, "two": 2}, db, protocol=2)

        with storage.PersistentDict(self.filename) as db:
            self.assertIn("one", db)
            self.assertIn("two", db)

        time.sleep(2)
        with storage.PersistentDict(self.filename, 1) as db:
            self.assertNotIn("one", db)
            self.assertNotIn("two", db)


class StorageList(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(StorageList, self).__init__(*args, **kwargs)
        self.filename = "listfile.pickle"
        self.path = os.path.join(storage.profile_dir, self.filename)

    def setUp(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_create_filename_part(self):
        with storage.PersistentList(self.filename) as db:
            self.assertFalse(db)
            self.assertIsNone(db._stream)

    def test_create_filename_full(self):
        with storage.PersistentList(self.path) as db:
            self.assertFalse(db)
            self.assertIsNone(db._stream)

    def test_flush_with_data(self):
        with storage.PersistentList(self.filename) as db:
            db.append("data")
            db.flush()
            self.assertIn("data", db)

    def test_flush_no_data(self):
        with storage.PersistentList(self.filename) as db:
            db.flush()

    def test_flush_with_missing_dir(self):
        shutil.rmtree(storage.profile_dir)
        with storage.PersistentList(self.filename) as db:
            db.append("data")
            db.flush()
            self.assertIn("data", db)

    def test_persistents(self):
        with storage.PersistentList(self.filename) as db:
            db.append("persistent")
            self.assertIn("persistent", db)

        with storage.PersistentList(self.filename) as db:
            db.append("persistent2")
            self.assertIn("persistent", db)
            self.assertIn("persistent2", db)

    def test_get(self):
        with storage.PersistentList(self.filename) as db:
            db.append("data")
            self.assertEqual(db[0], "data")

    def test_set(self):
        with storage.PersistentList(self.filename) as db:
            db.append("old")
            db[0] = "data"
            self.assertIn("data", db)
            self.assertEqual(db[0], "data")
            self.assertNotIn("old", db)

    def test_del(self):
        with storage.PersistentList(self.filename) as db:
            db.append("data")
            del db[0]
            self.assertNotIn("data", db)

    def test_insert(self):
        with storage.PersistentList(self.filename) as db:
            db.insert(0, "one")
            self.assertEqual(db[0], "one")

    def test_len(self):
        with storage.PersistentList(self.filename) as db:
            db.extend(["one", "two"])
            self.assertEqual(len(db), 2)

    def test_version_convert(self):
        with open(self.path, "wb") as db:
            pickle.dump(["one", "two"], db, protocol=2)

        with storage.PersistentList(self.filename) as db:
            self.assertIn("one", db)
            self.assertIn("two", db)

    def test_ttl(self):
        with open(self.path, "wb") as db:
            pickle.dump(["one", "two"], db, protocol=2)

        with storage.PersistentList(self.filename) as db:
            self.assertIn("one", db)
            self.assertIn("two", db)

        time.sleep(2)
        with storage.PersistentList(self.filename, 1) as db:
            self.assertNotIn("one", db)
            self.assertNotIn("two", db)
