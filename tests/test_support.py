import unittest


# Testing specific imports
from codequick import support, route
import xbmc


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
        support.base_logger.info("info")
        support.base_logger.debug("debug")
        support.base_logger.critical("crash")


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
        converted = self.route.args_to_kwargs(("True", False))
        self.assertListEqual(converted, [('one', 'True'), ('two', False)])

    def test_unittest_caller(self):
        ret = self.route.unittest_caller("one", two="two", return_data=True)
        self.assertTrue(ret)

    def test_unittest_caller_list(self):
        ret = self.route.unittest_caller("one", two="two", return_data=["data"])
        self.assertListEqual(ret, ["data"])


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = support.Dispatcher()
