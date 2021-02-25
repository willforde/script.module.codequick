from contextlib import contextmanager
import unittest
import logging
import inspect
import sys

# Testing specific imports
from codequick import support, route, script

PY3 = sys.version_info >= (3, 0)


@contextmanager
def mock_argv(argv):
    org_sys = sys.argv[:]
    sys.argv = argv
    try:
        yield
    finally:
        sys.argv = org_sys


class TestLogging(unittest.TestCase):
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
        self.route = support.Route(test_callback, route.Route, path, {})

    def test_unittest_caller(self):
        ret = self.route.unittest_caller("one", two="two", return_data=True)
        self.assertTrue(ret)

    def test_unittest_caller_list(self):
        ret = self.route.unittest_caller("one", two="two", return_data=["data"])
        self.assertListEqual(ret, ["data"])

    def test_unittest_caller_no_args(self):
        ret = self.route.unittest_caller()
        self.assertIsNone(ret, ["data"])

    def test_unittest_caller_error(self):
        def test_callback(_):
            raise RuntimeError

        path = test_callback.__name__.lower()
        route_obj = support.Route(test_callback, route.Route, path, {})

        with self.assertRaises(RuntimeError):
            route_obj.unittest_caller()


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = support.Dispatcher()

    def test_reset(self):
        self.dispatcher.selector = "test"
        self.dispatcher.params["tester"] = True
        self.dispatcher.registered_delayed.append("test")

        self.dispatcher.reset()
        self.assertEqual(self.dispatcher.selector, "root")
        self.assertListEqual(self.dispatcher.registered_delayed, [])
        self.assertDictEqual(self.dispatcher.params, dict())

    def test_parse_sysargs(self):
        dispatcher = support.Dispatcher()
        with mock_argv(["plugin://script.module.codequick/test/tester", 96, ""]):
            dispatcher.parse_args()

        self.assertEqual(dispatcher.selector, "/test/tester")

    def test_parse_sysargs_with_args(self):
        dispatcher = support.Dispatcher()
        with mock_argv(["plugin://script.module.codequick/test/tester", 96,
                        "?testdata=true&worker=false&_title_=test"]):
            dispatcher.parse_args()

        self.assertEqual(dispatcher.selector, "/test/tester")
        self.assertTrue(dispatcher.params.get("testdata") == "true")
        self.assertTrue(dispatcher.params.get("worker") == "false")
        self.assertTrue(dispatcher.params.get("_title_") == "test")
        self.assertTrue(dispatcher.callback_params.get("testdata") == "true")
        self.assertTrue(dispatcher.callback_params.get("worker") == "false")

    @unittest.skipIf(PY3, "The pickled string is specific to python 2")
    def test_parse_params_pickle_py2(self):
        dispatcher = support.Dispatcher()
        with mock_argv(["plugin://script.module.codequick/test/tester", 96,
                        "?_pickle_=80027d7100285506776f726b65727101895508746573746461746171028855075f7469746c655f710355"
                        "04746573747104752e"]):
            dispatcher.parse_args()

        self.assertEqual(dispatcher.selector, "/test/tester")
        self.assertTrue(dispatcher.params.get("testdata") is True)
        self.assertTrue(dispatcher.params.get("worker") is False)
        self.assertTrue(dispatcher.params.get("_title_") == "test")
        self.assertTrue(dispatcher.callback_params.get("testdata") is True)
        self.assertTrue(dispatcher.callback_params.get("worker") is False)

    @unittest.skipUnless(PY3, "The pickled string is specific to python 3")
    def test_parse_params_pickle_py3(self):
        dispatcher = support.Dispatcher()
        with mock_argv(["plugin://script.module.codequick/test/tester", 96,
                        "?_pickle_=8004952c000000000000007d94288c08746573746461746194888c06776f726b657294898c075f74697"
                        "46c655f948c047465737494752e"]):
            dispatcher.parse_args()

        self.assertEqual(dispatcher.selector, "/test/tester")
        self.assertTrue(dispatcher.params.get("testdata") is True)
        self.assertTrue(dispatcher.params.get("worker") is False)
        self.assertTrue(dispatcher.params.get("_title_") == "test")
        self.assertTrue(dispatcher.callback_params.get("testdata") is True)
        self.assertTrue(dispatcher.callback_params.get("worker") is False)

    def test_register_metacall(self):
        def root():
            pass

        self.dispatcher.register_delayed(root, [], {})
        self.assertListEqual(self.dispatcher.registered_delayed, [(root, [], {})])

    def test_metacalls(self):
        class Executed(object):
            yes = False

        def root():
            Executed.yes = True
            raise RuntimeError("should not be raised")

        self.dispatcher.register_delayed(root, [], {}, 0)
        self.dispatcher.run_delayed()
        self.assertTrue(Executed.yes)

    def test_register_root(self):
        def root():
            pass

        callback = self.dispatcher.register_callback(root, route.Route, {})
        self.assertIn("root", self.dispatcher.registered_routes)
        self.assertIsInstance(callback.route, support.Route)
        self.assertTrue(inspect.ismethod(callback.test))

    def test_register_non_root(self):
        def listing():
            pass

        callback = self.dispatcher.register_callback(listing, route.Route, {})
        self.assertIn("/tests/test_support/listing", self.dispatcher.registered_routes)
        self.assertIsInstance(callback.route, support.Route)
        self.assertTrue(inspect.ismethod(callback.test))

    def test_register_duplicate(self):
        def root():
            pass

        self.dispatcher.register_callback(root, route.Route, {})
        self.dispatcher.register_callback(root, route.Route, {})

    def test_dispatch(self):
        class Executed(object):
            yes = False

        def root(_):
            Executed.yes = True
            return False

        self.dispatcher.register_callback(root, route.Route, {})

        with mock_argv(["plugin://script.module.codequick", 96, ""]):
            self.dispatcher.run_callback()

        self.assertTrue(Executed.yes)

    def test_dispatch_script(self):
        class Executed(object):
            yes = False

        def root(_):
            Executed.yes = True
            return False

        self.dispatcher.register_callback(root, script.Script, {})
        self.dispatcher.run_callback()
        self.assertTrue(Executed.yes)

    def test_dispatch_fail(self):
        """Checks that error is caught and not raised."""
        class Executed(object):
            yes = False

        def root(_):
            Executed.yes = True
            raise RuntimeError("testing error")

        self.dispatcher.register_callback(root, route.Route, {})

        with mock_argv(["plugin://script.module.codequick", 96, ""]):
            self.dispatcher.run_callback()

        self.assertTrue(Executed.yes)

    def test_dispatch_fail_unicode_error(self):
        """Checks that error is caught and not raised."""
        class Executed(object):
            yes = False

        def root(_):
            Executed.yes = True
            raise RuntimeError(u"testing \xe9")

        self.dispatcher.register_callback(root, route.Route, {})
        with mock_argv(["plugin://script.module.codequick", 96, ""]):
            self.dispatcher.run_callback()

        self.assertTrue(Executed.yes)


class BuildPath(unittest.TestCase):
    def setUp(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def root(_, one=1, two=2):
            pass

        self.callback = root

    def tearDown(self):
        support.dispatcher.reset()
        del support.dispatcher.registered_routes["root"]

    def test_build_path_no_args(self):
        ret = support.build_path()
        self.assertEqual(ret, "plugin://script.module.codequick/root/")

    def test_build_new_path(self):
        ret = support.build_path(self.callback)
        self.assertEqual(ret, "plugin://script.module.codequick/root/")

    @unittest.skipIf(PY3, "The pickled string is specific to python 2")
    def test_build_path_new_args_py2(self):
        ret = support.build_path(self.callback, query={"testdata": "data"})
        self.assertEqual("plugin://script.module.codequick/root/?_pickle_="
                         "80027d71015508746573746461746171025504646174617103732e", ret)

    @unittest.skipUnless(PY3, "The pickled string is specific to python 2")
    def test_build_path_new_args_py3(self):
        ret = support.build_path(self.callback, query={"testdata": "data"})
        self.assertEqual("plugin://script.module.codequick/root/?_pickle_="
                         "80049516000000000000007d948c08746573746461746194"
                         "8c046461746194732e", ret)

    @unittest.skipIf(PY3, "The pickled string is specific to python 2")
    def test_build_path_extra_args_py2(self):
        support.dispatcher.params["_title_"] = "video"
        try:
            ret = support.build_path(self.callback, testdata="data")
            self.assertEqual("plugin://script.module.codequick/root/?_pickle_="
                             "80027d71012855075f7469746c655f71025505766964656"
                             "f71035508746573746461746171045504646174617105752e", ret)
        finally:
            del support.dispatcher.params["_title_"]

    @unittest.skipUnless(PY3, "The pickled string is specific to python 2")
    def test_build_path_extra_args_py3(self):
        support.dispatcher.params["_title_"] = "video"
        try:
            ret = support.build_path(self.callback, testdata="data")
            self.assertEqual("plugin://script.module.codequick/root/?_pickle_="
                             "80049529000000000000007d94288c075f7469746c655f94"
                             "8c05766964656f948c087465737464617461948c046461746194752e", ret)
        finally:
            del support.dispatcher.params["_title_"]
