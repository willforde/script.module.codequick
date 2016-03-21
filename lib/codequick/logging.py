# Kodi Imports
import collections
import xbmc

# Global Variables
devmode = False
addonID = None
logs = collections.defaultdict(list)

def dict_logs():
	mapping = {0:"debug",1:"info",2:"notice",3:"warning",4:"error",5:"severe",6:"fatal"}
	return {mapping[key]:value for key, value in logs.iteritems()}

def _log(msg, args, level=2):
	# Log message to kodi and builtin logger
	if args: msg = msg % args
	if isinstance(msg, unicode): msg = msg.encode("utf8")
	else: msg = str(msg)
	xbmc.log("[%s] %s" % (addonID, msg), level)
	logs[level].append(msg)

class logger(object):
	@staticmethod
	def debug(msg, *args):
		"""
		Write a string to kodi's log file and the debug window
		
		msg : string or unicode --- Message to log
		[*args] : string or unicode --- Arg values to add to string using string formatting
		"""
		_log(msg, args, 2 if devmode else 0)
	
	@staticmethod
	def info(msg, *args):
		"""
		Write a string to kodi's log file and the debug window
		
		msg : string or unicode --- Message to log
		[*args] : string or unicode --- Arg values to add to string using string formatting
		"""
		_log(msg, args, 2 if devmode else 1)
	
	@staticmethod
	def notice(msg, *args):
		"""
		Write a string to kodi's log file and the debug window
		
		msg : string or unicode --- Message to log
		[*args] : string or unicode --- Arg values to add to string using string formatting
		"""
		_log(msg, args, 2)
	
	@staticmethod
	def warning(msg, *args):
		"""
		Write a string to kodi's log file and the debug window
		
		msg : string or unicode --- Message to log
		[*args] : string or unicode --- Arg values to add to string using string formatting
		"""
		_log(msg, args, 3)
	
	@staticmethod
	def error(msg, *args):
		"""
		Write a string to kodi's log file and the debug window
		
		msg : string or unicode --- Message to log
		[*args] : string or unicode --- Arg values to add to string using string formatting
		"""
		_log(msg, args, 4)
	
	@staticmethod
	def severe(msg, *args):
		"""
		Write a string to kodi's log file and the debug window
		
		msg : string or unicode --- Message to log
		[*args] : string or unicode --- Arg values to add to string using string formatting
		"""
		_log(msg, args, 5)
	
	@staticmethod
	def fatal(msg, *args):
		"""
		Write a string to kodi's log file and the debug window
		
		msg : string or unicode --- Message to log
		[*args] : string or unicode --- Arg values to add to string using string formatting
		"""
		_log(msg, args, 6)
