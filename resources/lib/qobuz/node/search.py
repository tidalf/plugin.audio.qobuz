
from debug import info, warn, error
from flag import NodeFlag
from node import Node
import qobuz

class node_search(Node):

    def __init__(self, parent = None, params = None):
        super(node_search, self).__init__(parent, params)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_SEARCH

    def _get_xbmc_items(self, list, lvl, flag):

        stype = self.get_parameter('search-type')
        search = None
        limit = None
        if stype == 'songs':
            print "Searching songs"
            search = qobuz.core.getQobuzSearchTracks()
            limit = qobuz.addon.getSetting('songsearchlimit')
            heading = qobuz.lang(30013)
            self.set_content_type('songs')
        elif stype == 'albums':
            print "Searching albums"
            search = qobuz.core.getQobuzSearchAlbums()
            limit = qobuz.addon.getSetting('albumsearchlimit')
            heading = qobuz.lang(30014)
            self.set_content_type('albums')
        elif stype == 'artists':
            print "Searching artists"
            search = qobuz.core.getQobuzSearchArtists()
            limit = qobuz.addon.getSetting('artistsearchlimit')
            heading = qobuz.lang(30015)
            self.set_content_type('files')
        else:
            error(self, "Unknown search-type: " + stype)
        query = self.get_parameter('query')
        if not query:
            query = self._get_keyboard('', heading)
            if not query:
                return False
        query.strip()
        print "Query: " + query
        search.search(query, limit)
        slist = search.get_items()
        if len(slist) < 1:
            qobuz.gui.notification(36000, 35001)
            self._get_xbmc_items(list, lvl, flag)
            return False
        list.extend(slist)
        return True

    def _get_keyboard(self, default = "", heading = "", hidden = False):
        import xbmc
        kb = xbmc.Keyboard(default, heading, hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return unicode(kb.getText(), "utf-8")
        return ''
