# Standard Library Imports
import os

# Kodi Imports
import xbmcgui
import xbmc

# Package imports
from .support import strings, logger, args, get_info, set_setting, get_setting, localize
from .storage import DictStorage, SetStorage
from .utils import get_skin_name, Keyboard
from .api import ListItem

# Prerequisites
strings.update(custom=636, remove=1210, default=571,
               enter_number=611, enter_search_string=16017)


class ViewModeSelecter(object):
    """
    Class for displaying list of available skin view modes on the addon setting screen.

    Allowing for the selection of a view mode that will be force when
    displaying listitem content. Works with both video & folder views separately.

    Note
    ----
    Must be called from a script only.
    """

    def __init__(self):
        # Instance variables
        self.skinID = xbmc.getSkinDir()
        self.mode = args[u"arg1"]

        # Fetch database of skin codes
        skincode_path = os.path.join(get_info("path_global"), u"resources", u"data")
        try:
            database = DictStorage(skincode_path, u"skincodes.json")
        except (IOError, OSError) as e:
            logger.debug("Was unable to load skincodes databse: %s", repr(e))
            self.skin_codes = {}
        else:
            # Fetch codes for current skin and mode
            if self.skinID in database:
                self.skin_codes = self.filter_codes(database)
            else:
                logger.debug("No skin codes found for skin: %s", self.skinID)
                self.skin_codes = {}

    def set_mode(self, new_mode):
        """ Save new mode to addon setting

        Parameters
        ----------
        new_mode : unicode
            The new skin mode to use.
        """
        set_setting("%s.%s.view" % (self.skinID, str(self.mode)), new_mode)

    def filter_codes(self, database):
        """
        Filter codes down to current sky and mode

        Parameters
        ----------
        database : dict
            The database of skin ids and related view modes

        Returns
        -------
        dict
            The modes for the current skin
        """
        filterd = {}
        for mode, views in database[self.skinID].iteritems():
            if mode == self.mode or mode == u"both":
                for view in views:
                    key = localize(view[u"id"]) if view[u"id"] is not None else u""
                    if u"combine" in view:
                        key = u"%s %s" % (key, view[u"combine"])
                    filterd[key.strip()] = view[u"mode"]

        return filterd

    def display_modes(self):
        """
        Display list of viewmodes that are available and return user selection.

        Returns
        -------
        unicode
            The selected skin mode to use
        """

        # Fetch currently saved setting if it exists
        try:
            current_mode = get_setting("%s.%s.view" % (self.skinID, self.mode))
        except ValueError:
            current_mode = ""

        # Create list of item to show to user
        reference = [None]
        show_list = [localize("default")]
        for name, mode in self.skin_codes.iteritems():
            reference.append(mode)
            if current_mode and current_mode == mode:
                show_list.append(u"[B]-%s[/B]" % name)
            else:
                show_list.append(name)

        # Append custom option to showlist including current mode if its custom
        if current_mode and current_mode not in self.skin_codes.values():
            custom = u"[B]-%s (%i)[/B]" % (localize("custom"), current_mode)
        else:
            custom = localize("custom")
        show_list.append(custom)

        # Display List to User
        dialog = xbmcgui.Dialog()
        ret = dialog.select(get_skin_name(self.skinID), show_list)
        if ret == 0:
            logger.debug("Reseting viewmode setting to default")
            return u""
        elif ret == len(show_list) - 1:
            new_mode = self.ask_for_view_id(current_mode)
            if new_mode:
                logger.debug("Saving new custom viewmode setting: %s", new_mode)
            return new_mode
        elif ret > 0:
            new_mode = unicode(reference[ret])
            logger.debug("Saving new viewmode setting: %s", new_mode)
            return new_mode

    def ask_for_view_id(self, current_mode):
        """
        Ask the user what custom view mode to use.

        Parameters
        ----------
        current_mode : int
            The current set mode

        Returns
        -------
        unicode, optional
            The new custom viewmode.
        """
        dialog = xbmcgui.Dialog()
        ret = dialog.numeric(0, self.localize("enter_number"), str(current_mode))
        if ret:
            return unicode(ret)
        else:
            return None


class SavedSearches(object):
    """
    Class used to list all saved searches for the addon that called it.
    Usefull to add search support to addon that will also keep track of previous searches
    Also contains option via context menu to remove old search terms.
    """
    searches = None

    def start(self):
        """
        List all saved searches

        Returns
        -------
        gen
            A generator of (path, listitem, isFolder) tuples
        """
        # Fetch list of current saved searches
        self.searches = searches = SetStorage(get_info("profile"), u"searchterms.json")

        # Remove term from saved searches if remove argument was passed
        if args.get("remove") in searches:
            searches.remove(args.pop("remove"))
            searches.sync()

        # Show search dialog if search argument was passed or there is not search term saved
        elif not searches or args.pop("search", None) is not None:
            self.search_dialog()

        # List all saved search terms
        try:
            return self.list_terms()
        finally:
            searches.close()

    def search_dialog(self):
        """ Show dialog for user to enter a new search term """
        ret = Keyboard("", localize("enter_search_string"), False)
        if ret:
            # Add searchTerm to database
            self.searches.add(ret)
            self.searches.sync()

    def list_terms(self):
        """
        List all saved search terms.

        Yield
        -------
        tuple
            A listitem tuple of (path, listitem, isFolder).
        """

        # Create Speed vars
        base_url = args[u"url"]
        farwarding_route = args[u"route"]

        # Add search listitem entry
        item = ListItem()
        item.label = u"[B]%s[/B]" % localize("search")
        query = args.copy()
        query["search"] = "true"
        query["updatelisting"] = "true"
        query["cachetodisc"] = "true"
        item.url.update(query)
        yield item.get_tuple(saved_searches)

        # Create Context Menu item Params
        str_remove = localize("remove")
        query_cx = args.copy()
        query_li = args.copy()

        # Loop earch search item
        for searchTerm in self.searches:
            # Create listitem of Data
            item = ListItem()
            item.label = searchTerm.title()
            query_li["url"] = base_url % searchTerm
            item.url.update(query_li)

            # Creatre Context Menu item to remove search item
            query_cx["remove"] = searchTerm
            item.context.menu_update(saved_searches, str_remove, **query_cx)

            # Return Listitem data
            yield item.get_tuple(farwarding_route)
