#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
import qobuz
from node.flag import NodeFlag
from debug import info, warn, error, debug
import pprint

class IRenderer(object):

    def __init__(self, node_type, node_id = None):
        self.node_type = node_type
        self.node_id = node_id
        self.root = None
        self.filter = NodeFlag.TYPE_NODE

    def to_s(self):
        return pprint.pformat(self)

    def set_depth(self, d):
        self.depth = d

    def set_filter(self, filter):
        self.filter = filter

    def set_root_node(self):
        root = None
        if self.node_type & NodeFlag.TYPE_ROOT:
            from node.root import Node_root
            root = Node_root(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_TRACK:
            from node.track import Node_track
            root = Node_track(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_USERPLAYLISTS:
            from node.user_playlists import Node_user_playlists
            root = Node_user_playlists(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PLAYLIST:
            from node.playlist import Node_playlist
            root = Node_playlist(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_RECOMMENDATION:
            from node.recommendation import Node_recommendation
            root = Node_recommendation(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PRODUCT:
            from node.product import Node_product
            root = Node_product(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PURCHASES:
            from node.purchases import Node_purchases
            root = Node_purchases(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_SEARCH:
            from node.search import Node_search
            root = Node_search(None, qobuz.boot.params)
            root.set_search_type(qobuz.boot.params['search-type'])
        elif self.node_type & NodeFlag.TYPE_ARTIST:
            from node.artist import Node_artist
            root = Node_artist(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_SIMILAR_ARTIST:
            from node.similar_artists import Node_similar_artist
            root = Node_similar_artist(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_FAVORITES:
            from node.favorites import Node_favorites
            root = Node_favorites(None, qobuz.boot.params)
        else:
            warn(self, "Cannot set root node!")
            return False
        root.set_id(self.node_id)
        root.get_url()
        self.root = root
        return True
