# -*- coding: utf-8 -*-

# Package imports
from .base import dispatcher
from .storage import PersistentList
from .listing import Listitem
from .utils import keyboard
from .api import Route

# Prerequisites
ENTER_SEARCH_STRING = 16017
REMOVE = 1210
SEARCH = 137


@Route.register
class SavedSearches(Route):
    """
    Class used to list all saved searches for the addon that called it.
    Usefull to add search support to addon that will also keep track of previous searches
    Also contains option via context menu to remove old search terms.
    """
    
    def __init__(self):
        super(SavedSearches, self).__init__()

        # List of current saved searches
        self.search_db = PersistentList(u"_searches_.json")

    def run(self, remove=None, search=False, **extras):
        """List all saved searches"""

        # Set update listing to True only when change state of searches
        if remove or search:
            self.update_listing = True

        # Remove term from saved searches if remove argument was passed
        if remove in self.search_db:
            self.search_db.remove(remove)
            self.search_db.flush()

        # Show search dialog if search argument was passed or if there is no search term saved
        elif not self.search_db or search:
            self.search_dialog()

        # List all saved search terms
        return self.list_terms(extras)

    def search_dialog(self):
        """Show dialog for user to enter a new search term."""
        search_term = keyboard(self.localize(ENTER_SEARCH_STRING))
        if search_term and search_term not in self.search_db:
            self.search_db.append(search_term)
            self.search_db.flush()

    def list_terms(self, extras):
        """:rtype: :class:`types.GeneratorType`"""
        # Add search listitem
        search_item = Listitem()
        search_item.label = u"[B]%s[/B]" % self.localize(SEARCH)
        search_item.set_callback(self, search=True, **extras)
        search_item.art.global_thumb(u"search_new.png")
        yield search_item

        callback = dispatcher[extras["route"]].callback
        callback_params = extras.copy()
        del callback_params["route"]

        # Create Context Menu item requirements
        str_remove = self.localize(REMOVE)

        # Add all saved searches to item list
        for search_term in self.search_db:
            item = Listitem()
            item.label = search_term.title()

            # Creatre Context Menu item for removing search term
            item.context.container(str_remove, self, remove=search_term, **extras)

            # Update params with full url and set the callback
            item.params.update(callback_params, search_query=search_term)
            item.set_callback(callback)
            yield item

        # Finished with the search database
        self.search_db.close()
