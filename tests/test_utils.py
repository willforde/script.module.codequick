from addondev import testing
import unittest
import types

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

    def test_keyboard(self):
        with testing.mock_keyboard("Testing input"):
            ret = utils.keyboard("Test")

        self.assertEqual(ret, "Testing input")

    def test_bold(self):
        test_string = "text"
        ret = utils.bold(test_string)
        self.assertEqual("[B]text[/B]", ret, msg="Text was not bolded")
        self.assertIsInstance(ret, type(test_string), msg="Text type was unexpectedly converted")

    def test_bold_uni(self):
        test_string = u"text"
        ret = utils.bold(test_string)
        self.assertEqual("[B]text[/B]", ret, msg="Text was not bolded")
        self.assertIsInstance(ret, type(test_string), msg="Text type was unexpectedly converted")

    def test_italic(self):
        test_string = "text"
        ret = utils.italic(test_string)
        self.assertEqual("[I]text[/I]", ret, msg="Text was not italic")
        self.assertIsInstance(ret, type(test_string), msg="Text type was unexpectedly converted")

    def test_italic_uni(self):
        test_string = u"text"
        ret = utils.italic(test_string)
        self.assertEqual("[I]text[/I]", ret, msg="Text was not italic")
        self.assertIsInstance(ret, type(test_string), msg="Text type was unexpectedly converted")

    def test_color(self):
        test_string = "text"
        ret = utils.color(test_string, color_code="red")
        self.assertEqual("[COLOR red]text[/COLOR]", ret, msg="Text was not colorized")
        self.assertIsInstance(ret, type(test_string), msg="Text type was unexpectedly converted")

    def test_color_uni(self):
        test_string = u"text"
        ret = utils.color(test_string, color_code="red")
        self.assertEqual("[COLOR red]text[/COLOR]", ret, msg="Text was not colorized")
        self.assertIsInstance(ret, type(test_string), msg="Text type was unexpectedly converted")
