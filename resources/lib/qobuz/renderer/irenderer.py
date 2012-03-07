# -*- coding: UTF-8 -*- 
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
from debug import info, warn

class IRenderer(object):

    def __init__(self, node_type, node_id = None, flag = 0):
        self.node_type = node_type
        self.node_id = node_id
        self.flag = flag
        self.root = None

    def to_s(self):
        s = "Node type: " + str(self.node_type) + "\n"
        s += "Node id  : " + str(self.node_id) + "\n"
        s += "Flag     : " + str(self.flag) + "\n"
        if self.root:
            s += self.root.to_s()
        return s

    def set_root_node(self):
        root = None
        if self.node_type & NodeFlag.TYPE_ROOT:
            from node.root import Node_root
            root = Node_root(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_TRACK:
            from node_track import node_track
            root = node_track(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_USERPLAYLISTS:
            print "SET ROOT NODE: USER PLAYLISTS"
            from node.user_playlists import Node_user_playlists
            root = Node_user_playlists(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PLAYLIST:
            print "SET ROOT NODE: PLAYLIST"
            from node.playlist import Node_playlist
            root = Node_playlist(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_RECOMMANDATION:
            from node.recommendation import Node_recommendation
            root = Node_recommendation(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PRODUCT:
            print "Render product"
            from node.product import Node_product
            root = Node_product(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_VIRTUAL_PLAYLIST:
            from node_virtual_playlist import node_virtual_playlist
            root = node_virtual_playlist(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_PURCHASES:
            from node_purchases import node_purchases
            root = node_purchases(None, qobuz.boot.params)
        elif self.node_type & NodeFlag.TYPE_SEARCH:
            from node_search import node_search
            root = node_search(None, qobuz.boot.params)
        else:
            print "Nothing to display"
            return False
        root.set_id(self.node_id)
        root.set_url()
        self.root = root
        return True
