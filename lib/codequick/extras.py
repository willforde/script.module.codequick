# Standard Library Imports
import os

# Kodi Imports
import xbmcgui
import xbmc

# Package imports
from .inheritance import VirtualFS
from .api import Base, route, localized

# Prerequisites
localized({"Default":571, "Enter_number":611, "Custom":636, "Search":137, "Remove":1210, "Enter_search_string":16017})

@route("/internal/setViewMode")
class viewModeSelecter(Base):
	"""
	Class for displaying list of available skin view modes.
	Allowing for the selection of a view mode that will be force when
	displaying listitem content. Works with both video & folder views separately
	
	NOTE
	Must be called as a script only
	"""
	
	def __init__(self):
		# Instance variables
		self.skinID = xbmc.getSkinDir()
		self.mode = self[u"arg1"]
		
		# Fetch databse of skin codes
		skincodePath = os.path.join(self._path_global, u"resources", u"data", u"skincodes.json")
		try: database = self.dictStorage(skincodePath)
		except (IOError, OSError) as e:
			self.debug("Was unable to load skincodes databse: %s", repr(e))
			skinCodes = {}
		else:
			# Fetch codes for current skin and mode
			if self.skinID in database: skinCodes = self.filter_codes(database)
			else:
				self.debug("No skin codes found for skin: %s", self.skinID)
				skinCodes = {}
		
		# Display list of view modes available
		newMode = self.display(skinCodes)
		
		# Save new mode to setting
		if newMode is not None: self.setSetting("%s.%s.view" % (self.skinID, self.mode), newMode)
	
	def filter_codes(self, database):
		""" Filter codes down to current sky and mode """
		filterd = {}
		for mode, views in database[self.skinID].iteritems():
			if mode == self.mode or mode == u"both":
				for view in views:
					key = self.getLocalizedString(view[u"id"]) if view[u"id"] is not None else u""
					if u"combine" in view: key = u"%s %s" % (key, view[u"combine"])
					filterd[key.strip()] = view[u"mode"]
		
		return filterd
	
	def display(self, skinCodes):
		""" Display list of viewmodes that are available and return user selection """
		
		# Fetch currently saved setting if it exists
		try: currentMode = self.getSetting("%s.%s.view" % (self.skinID, self.mode))
		except ValueError: currentMode = ""
		
		# Create list of item to show to user
		reference = [None]
		showList = [self.getLocalizedString("Default")]
		for name, mode in skinCodes.iteritems():
			reference.append(mode)
			if currentMode and currentMode == mode:
				showList.append(u"[B]-%s[/B]" % name)
			else:
				showList.append(name)
		
		# Append custom option to showlist including current mode if its custom
		if currentMode and currentMode not in skinCodes.values(): custom = u"[B]-%s (%i)[/B]" % (self.getLocalizedString("Custom"), currentMode)
		else: custom = self.getLocalizedString("Custom")
		showList.append(custom)
		
		# Display List to User
		dialog = xbmcgui.Dialog()
		ret = dialog.select(self.utils.get_skin_name(self.skinID), showList)
		if ret == 0:
			self.debug("Reseting viewmode setting to default")
			return ""
		elif ret == len(showList) - 1:
			newMode = self.askForViewID(currentMode)
			if newMode: self.debug("Saving new custom viewmode setting: %s", newMode)
			return newMode
		elif ret > 0:
			newMode = str(reference[ret])
			self.debug("Saving new viewmode setting: %s", newMode)
			return newMode
	
	def askForViewID(self, currentMode):
		""" Ask the user what custom view mode to use """
		dialog = xbmcgui.Dialog()
		ret = dialog.numeric(0, self.getLocalizedString("Enter_number"), str(currentMode))
		if ret: return str(ret)
		else: return None


@route("/internal/SavedSearches")
class SavedSearches(VirtualFS):
	"""
	Class used to list all saved searches for the addon that called it.
	Usefull to add search support to addon that will also keep track of previous searches
	Also contains option via context menu to remove old search terms.
	"""
	
	def start(self):
		# Fetch list of current saved searches
		self.searches = searches = self.setStorage(u"searchterms.json")
		
		# Remove term from saved searches if remove argument was passed
		if self.get("remove") in searches:
			searches.remove(self.pop("remove"))
			searches.sync()
		
		# Show search dialog if search argument was passed or there is not search term saved
		elif not searches or self.pop("search", None) is not None:
			self.search_dialog()
		
		# List all saved search terms
		try: return self.list_terms()
		finally: searches.close()
	
	def search_dialog(self):
		""" Show dialog for user to enter a new search term """
		ret = self.utils.Keyboard("", self.getLocalizedString("Enter_search_string"), False)
		if ret:
			# Add searchTerm to database
			self.searches.add(ret)
			self.searches.sync()
	
	def list_terms(self):
		""" List all saved search terms """
		
		# Create Speed vars
		baseUrl = self["url"]
		listitem = self.listitem
		farwarding_route = self[u"route"]
		
		# Add search listitem entry
		item = listitem()
		item.setLabel(u"[B]%s[/B]" % self.getLocalizedString("Search"))
		query = self.copy()
		query["search"] = "true"
		query["updatelisting"] = "true"
		query["cachetodisc"] = "true"
		item.update(query)
		yield item.get(self)
		
		# Create Context Menu item Params
		strRemove = self.getLocalizedString("Remove")
		queryCx = self.copy()
		queryLi = self.copy()
		
		# Loop earch Search item
		for searchTerm in self.searches:
			# Create listitem of Data
			item = listitem()
			item.setLabel(searchTerm.title())
			queryLi["url"] = baseUrl % searchTerm			
			item.update(queryLi)
			
			# Creatre Context Menu item to remove search item
			queryCx["remove"] = searchTerm
			item.menu_update(self, strRemove, **queryCx)
			
			# Return Listitem data
			yield item.get_route(farwarding_route)
