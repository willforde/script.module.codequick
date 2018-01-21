import unittest
import logging
import sys

# Testing specific imports
from codequick import support, route
import xbmc

PY3 = sys.version_info >= (3, 0)


class TestLogging(unittest.TestCase):
    def test_logger_map(self):
        logmap = support.LoggingMap()
        ret = logmap[55]
        self.assertEqual(ret, xbmc.LOGNOTICE)

    def test_logger(self):
        support.base_logger.debug("test debug")
        self.assertIn("[root] test debug", support.kodi_logger.debug_msgs)

    # noinspection PyMethodMayBeStatic
    def test_critical(self):
        logger = logging.getLogger()
        logger.disabled = False

        try:
            support.base_logger.info("info")
            support.base_logger.debug("debug")
            support.base_logger.critical("crash")
        finally:
            logger.disabled = False


class TestRoute(unittest.TestCase):
    def setUp(self):
        # noinspection PyUnusedLocal
        def test_callback(_, one=1, two="2", return_data=None):
            return return_data

        path = test_callback.__name__.lower()
        self.route = support.Route(route.Route, test_callback, test_callback, path)

    def test_arg_names(self):
        args = self.route.arg_names()
        self.assertListEqual(args, ['_', 'one', 'two', 'return_data'])

    def test_args_to_kwargs(self):
        converted = list(self.route.args_to_kwargs(("True", False)))
        self.assertEqual(len(converted), 2)
        self.assertTupleEqual(converted[0], ("one", "True"))
        self.assertTupleEqual(converted[1], ("two", False))

    def test_unittest_caller(self):
        ret = self.route.unittest_caller("one", two="two", return_data=True)
        self.assertTrue(ret)

    def test_unittest_caller_list(self):
        ret = self.route.unittest_caller("one", two="two", return_data=["data"])
        self.assertListEqual(ret, ["data"])

    def test_unittest_caller_no_args(self):
        ret = self.route.unittest_caller()
        self.assertIsNone(ret, ["data"])


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = support.Dispatcher()

    def test_reset(self):
        self.dispatcher.selector = "test"
        self.dispatcher.params["tester"] = True
        self.dispatcher.metacalls.append("test")

        self.dispatcher.reset()
        self.assertEqual(self.dispatcher.selector, "root")
        self.assertListEqual(self.dispatcher.metacalls, [])
        self.assertDictEqual(self.dispatcher.params, dict())

    def test_parse_sysargs(self):
        org_sys = sys.argv[:]
        sys.argv = ["plugin://script.module.codequick/test/tester", 96, ""]
        try:
            self.dispatcher.parse_sysargs()
        finally:
            sys.argv = org_sys

        self.assertEqual(self.dispatcher.handle, 96)
        self.assertEqual(self.dispatcher.selector, "test/tester")

    def test_parse_sysargs_with_args(self):
        org_sys = sys.argv[:]
        sys.argv = ["plugin://script.module.codequick/test/tester", 96, "?testdata=true&worker=false&_title_=test"]
        try:
            self.dispatcher.parse_sysargs()
        finally:
            sys.argv = org_sys

        self.assertEqual(self.dispatcher.handle, 96)
        self.assertEqual(self.dispatcher.selector, "test/tester")
        self.assertDictContainsSubset(self.dispatcher.params,
                                      {"testdata": "true", "worker": "false", "_title_": "test"})
        self.assertDictContainsSubset(self.dispatcher.support_params, {"_title_": "test"})
        self.assertDictContainsSubset(self.dispatcher.callback_params, {"testdata": "true", "worker": "false"})

    def test_parse_sysargs_error(self):
        org_sys = sys.argv[:]
        sys.argv = ["script://script.module.codequick", 96, ""]
        try:
            with self.assertRaises(RuntimeError):
                self.dispatcher.parse_sysargs()
        finally:
            sys.argv = org_sys

    @unittest.skipIf(PY3, "The pickled string is specific to python 2")
    def test_parse_params_pickle_py2(self):
        self.dispatcher.parse_params(
            "_pickle_=80027d7100285506776f726b65727101895508746573746461746171028855075f7469746c655f71035"
            "504746573747104752e")
        self.assertDictContainsSubset(self.dispatcher.params,
                                      {"testdata": True, "worker": False, "_title_": "test"})
        self.assertDictContainsSubset(self.dispatcher.support_params, {"_title_": "test"})
        self.assertDictContainsSubset(self.dispatcher.callback_params, {"testdata": True, "worker": False})

    @unittest.skipUnless(PY3, "The pickled string is specific to python 3")
    def test_parse_params_pickle_py3(self):
        self.dispatcher.parse_params(
            "_pickle_=8004952c000000000000007d94288c08746573746461746194888c06776f726b657294898c075f74697"
            "46c655f948c047465737494752e")
        self.assertDictContainsSubset(self.dispatcher.params,
                                      {"testdata": True, "worker": False, "_title_": "test"})
        self.assertDictContainsSubset(self.dispatcher.support_params, {"_title_": "test"})
        self.assertDictContainsSubset(self.dispatcher.callback_params, {"testdata": True, "worker": False})
