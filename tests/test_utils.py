from addondev import testing
import unittest
import types
import sys

# Testing specific imports
from codequick import utils


class Utils(unittest.TestCase):
    def test_ensure_unicode_with_bytes(self):
        ret = utils.ensure_unicode(b"teststring")
        self.assertIsInstance(ret, utils.unicode_type)
        self.assertEqual(ret, u"teststring")

    def test_ensure_unicode_with_unicode(self):
        ret = utils.ensure_unicode(u"teststring")
        self.assertIsInstance(ret, utils.unicode_type)
        self.assertEqual(ret, u"teststring")

    def test_ensure_bytes_with_bytes(self):
        ret = utils.ensure_bytes(b"teststring")
        self.assertIsInstance(ret, bytes)
        self.assertEqual(ret, b"teststring")

    def test_ensure_bytes_with_unicode(self):
        ret = utils.ensure_bytes(u"teststring")
        self.assertIsInstance(ret, bytes)
        self.assertEqual(ret, b"teststring")

    def test_ensure_native_str_with_bytes(self):
        ret = utils.ensure_native_str(b"teststring")
        self.assertIsInstance(ret, str)
        self.assertEqual(ret, "teststring")

    def test_ensure_native_str_with_unicode(self):
        ret = utils.ensure_native_str(u"teststring")
        self.assertIsInstance(ret, str)
        self.assertEqual(ret, "teststring")

    def test_ensure_native_str_with_int(self):
        ret = utils.ensure_native_str(101)
        self.assertIsInstance(ret, str)
        self.assertEqual(ret, "101")

    def test_safe_path_bytes(self):
        ret = utils.safe_path(b"teststring")
        if sys.platform.startswith("win"):
            self.assertIsInstance(ret, utils.unicode_type)
        else:
            self.assertIsInstance(ret, bytes)

    def test_safe_path_unicode(self):
        ret = utils.safe_path(u"teststring")
        if sys.platform.startswith("win"):
            self.assertIsInstance(ret, utils.unicode_type)
        else:
            self.assertIsInstance(ret, bytes)

    def test_strip_tags(self):
        ret = utils.strip_tags('<a href="http://example.com/">I linked to <i>example.com</i></a>')
        self.assertEqual(ret, "I linked to example.com")

    def test_urljoin_partial(self):
        url_constructor = utils.urljoin_partial("https://google.ie/")
        self.assertIsInstance(url_constructor, types.FunctionType)
        ret = url_constructor("/gmail")
        self.assertEqual(ret, "https://google.ie/gmail")

    def test_parse_qs_full(self):
        ret = utils.parse_qs("http://example.com/path?q=search&safe=no")
        self.assertIsInstance(ret, dict)
        self.assertDictEqual(ret, {u"q": u"search", u"safe": u"no"})

    def test_parse_qs_part(self):
        ret = utils.parse_qs("q=search&safe=no")
        self.assertIsInstance(ret, dict)
        self.assertDictEqual(ret, {u"q": u"search", u"safe": u"no"})

    def test_parse_qs_fail(self):
        with self.assertRaises(ValueError):
            utils.parse_qs("q=search&safe=no&safe=yes")

    def test_CacheProperty(self):
        import random

        class Test(object):
            @utils.CacheProperty
            def data_id(self):
                return random.random()

        obj = Test()
        first_no = obj.data_id
        self.assertIsInstance(first_no, float)
        self.assertEqual(obj.data_id, first_no)
        ret = Test.data_id
        self.assertIsInstance(ret, utils.CacheProperty)

    def test_keyboard(self):
        with testing.mock_keyboard("Testing input"):
            ret = utils.keyboard("Test")

        self.assertEqual(ret, "Testing input")
