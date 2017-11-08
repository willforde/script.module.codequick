from addondev import initializer
import os

initializer(os.path.join(os.path.dirname(os.path.dirname(__file__)), "script.module.codequick"))
import unittest
from codequick import utils

print ("Testing %s" % os.getcwd())


class Utils(unittest.TestCase):
    def test_ensure_unicode_with_bytes(self):
        ret = utils.ensure_unicode(b"teststring")
        self.assertIsInstance(ret, utils.unicode_type)
        self.assertEqual(ret, u"teststring")

    def test_ensure_unicode_with_unicode(self):
        ret = utils.ensure_unicode(u"teststring")
        self.assertIsInstance(ret, utils.unicode_type)
        self.assertEqual(ret, u"teststring")
