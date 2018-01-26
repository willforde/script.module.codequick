from addondev.testing import data_log
import unittest

from codequick import script


class Addon(object):
    def __init__(self, id=u"testdata"):
        self.settings = {}
        self.default = id

    def getSetting(self, id):
        return type(u"")(self.settings.get(id, self.default))

    def setSetting(self, id, value):
        self.settings[id] = value


class MockLogger(object):
    def __init__(self):
        self.record = ""
        self.lvl = 0

        self.org_logger = script.addon_logger
        script.addon_logger = self

    def log(self, lvl, msg, *args):
        self.lvl = lvl
        if args:
            self.record = msg % args
        else:
            self.record = msg

    def __enter__(self):
        return self

    def __exit__(self, *_):
        script.addon_logger = self.org_logger


class Settings(unittest.TestCase):
    def setUp(self):
        self.org_addon_data = script.addon_data
        self.org_xbmcaddon = script.xbmcaddon.Addon

        script.addon_data = Addon()
        script.xbmcaddon.Addon = Addon

        self.settings = script.Settings()

    def tearDown(self):
        script.addon_data = self.org_addon_data
        script.xbmcaddon.Addon = self.org_xbmcaddon

    def test_getter(self):
        string = self.settings["tester"]
        self.assertEqual(string, "testdata")

    def test_setter(self):
        self.settings["tester"] = "newdata"
        string = self.settings["tester"]
        self.assertEqual(string, "newdata")

    def test_deleter(self):
        self.settings["tester"] = "newdata"
        del self.settings["tester"]
        string = self.settings["tester"]
        self.assertEqual(string, "")

    def test_get_string(self):
        self.settings["tester"] = "newdata"
        data = self.settings.get_string("tester")
        self.assertIsInstance(data, type(u""))
        self.assertEqual(data, "newdata")

    def test_get_boolean(self):
        self.settings["tester"] = "true"
        data = self.settings.get_boolean("tester")
        self.assertIsInstance(data, bool)
        self.assertEqual(data, True)

    def test_get_int(self):
        self.settings["tester"] = "999"
        data = self.settings.get_int("tester")
        self.assertIsInstance(data, int)
        self.assertEqual(data, 999)

    def test_get_number(self):
        self.settings["tester"] = "1.5"
        data = self.settings.get_number("tester")
        self.assertIsInstance(data, float)
        self.assertEqual(data, 1.5)

    def test_get_string_addon(self):
        data = self.settings.get_string("tester", addon_id="newdata")
        self.assertIsInstance(data, type(u""))
        self.assertEqual(data, "newdata")

    def test_get_boolean_addon(self):
        data = self.settings.get_boolean("tester", addon_id="true")
        self.assertIsInstance(data, bool)
        self.assertEqual(data, True)

    def test_get_int_addon(self):
        data = self.settings.get_int("tester", addon_id="999")
        self.assertIsInstance(data, int)
        self.assertEqual(data, 999)

    def test_get_number_addon(self):
        data = self.settings.get_number("tester", addon_id="1.5")
        self.assertIsInstance(data, float)
        self.assertEqual(data, 1.5)


class Script(unittest.TestCase):
    def setUp(self):
        self.script = script.Script()

    def test_register_metacall(self):
        def tester():
            pass

        self.script.register_metacall(tester)
        for callback, _, _ in script.dispatcher.metacalls:
            if callback is tester:
                self.assertTrue(True, "")
                break
        else:
            self.assertTrue(False)

    def test_log_noarg(self):
        with MockLogger() as logger:
            self.script.log("test msg")
            self.assertEqual(logger.record, "test msg")

    def test_log_noarg_lvl(self):
        with MockLogger() as logger:
            self.script.log("test msg", lvl=20)
            self.assertEqual(logger.record, "test msg")
            self.assertEqual(logger.lvl, 20)

    def test_log_args(self):
        with MockLogger() as logger:
            self.script.log("test %s", ["msg"])
            self.assertEqual(logger.record, "test msg")

    def test_notify(self):
        self.script.notify("test header", "test msg", icon=self.script.NOTIFY_INFO)
        data = data_log["notifications"][-1]
        self.assertEqual(data[0], "test header")
        self.assertEqual(data[1], "test msg")
        self.assertEqual(data[2], "info")

    def test_localize(self):
        self.assertEqual(self.script.localize(30001), "")

    def test_localize_novideo(self):
        self.assertEqual(self.script.localize(32401), "No video found!")

    def test_localize_nodata(self):
        self.assertEqual(self.script.localize(33077), "No data found!")

    def test_get_author(self):
        self.assertEqual(self.script.get_info("author"), "willforde")

    def test_get_changelog(self):
        self.assertEqual(self.script.get_info("changelog"), "")

    def test_get_description(self):
        self.assertTrue(self.script.get_info("description").startswith(
            "Codequick is a framework for kodi add-on's. The goal of this"))

    def test_get_disclaimer(self):
        self.assertEqual(self.script.get_info("disclaimer"), "")

    def test_get_fanart(self):
        self.assertTrue(self.script.get_info("fanart").endswith("script.module.codequick/fanart.jpg"))

    def test_get_icon(self):
        self.assertTrue(self.script.get_info("icon").endswith("script.module.codequick/resources/icon.png"))

    def test_get_id(self):
        self.assertEqual(self.script.get_info("id"), "script.module.codequick")

    def test_get_name(self):
        self.assertEqual(self.script.get_info("name"), "CodeQuick")

    def test_get_path(self):
        self.assertTrue(self.script.get_info("path").endswith("script.module.codequick"))

    def test_get_profile(self):
        self.assertTrue(self.script.get_info("profile").endswith("userdata/addon_data/script.module.codequick"))

    def test_get_stars(self):
        self.assertEqual(self.script.get_info("stars"), "-1")

    def test_get_summary(self):
        self.assertEqual(self.script.get_info("summary"), "Framework for creating kodi add-on's.")

    def test_get_type(self):
        self.assertEqual(self.script.get_info("type"), "xbmc.python.module")

    def test_get_version(self):
        self.assertIsInstance(self.script.get_info("version"), type(u""))

    def test_get_name_addon(self):
        self.assertEqual(self.script.get_info("name", addon_id="script.module.codequick"), "CodeQuick")

    def test_request(self):
        req = self.script.request
        self.assertIsInstance(req, script.urlquick.Session)

    def test_icon(self):
        self.assertTrue(self.script.icon.endswith("script.module.codequick/resources/icon.png"))

    def test_fanart(self):
        self.assertTrue(self.script.fanart.endswith("script.module.codequick/fanart.jpg"))

    def test_profile(self):
        self.assertTrue(self.script.profile.endswith("userdata/addon_data/script.module.codequick"))

    def test_path(self):
        self.assertTrue(self.script.path.endswith("script.module.codequick"))
