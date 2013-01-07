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
import xbmcgui

import qobuz
from flag import NodeFlag as Flag
from inode import INode
from product import Node_product
from debug import warn, log
from gui.util import lang
from gui.util import getImage, notifyH
from util import getRenderer
from api import api
'''
    @class Node_favorites:
'''
from track import Node_track

import pprint

class Node_favorites(INode):

    def __init__(self, parent=None, parameters=None, progress=None):
        super(Node_favorites, self).__init__(parent, parameters)
        self.type = Flag.FAVORITES
        self.set_label(lang(30079))
        self.name = lang(30079)
        self.label = lang(30079)
        self.content_type = 'albums'
        self.image = getImage('favorites')
        self.offset = self.get_parameter('offset') or 0
        
    def pre_build_down(self, Dir, lvl, whiteFlag, blackFlag):
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(
            name='user-favorites', limit=limit, offset=self.offset)
        if not data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        self.data = data['data']
        return True

    def _build_down(self, Dir, lvl, whiteFlag, blackFlag):
        if 'albums' in self.data:
            self._build_down_albums(Dir, lvl, whiteFlag, blackFlag)
        if 'tracks' in self.data:
            self._build_down_tracks(Dir, lvl, whiteFlag, blackFlag)
        return True
        
    def _build_down_tracks(self, Dir, lvl, whiteFlag, blackFlag):
        for track in self.data['tracks']['items']:
            node = Node_track()
            node.data = track
            self.add_child(node)

    def _build_down_albums(self, Dir, lvl, whiteFlag, blackFlag):
        for album in self.data['albums']['items']:
            node = Node_product()
            node.data = album
            self.add_child(node)


    def get_description(self):
        return self.get_property('description')

    def gui_add_albums(self):
        heading = 'Qobuz Favorites (i8n)'
        qnt = int(self.get_parameter('qnt'))
        qid = self.get_parameter('qid')
        nodes = self.list_albums(qnt, qid)
        if len(nodes) == 0:
            notifyH(heading, 'Nothing to add')
            return False
        ret = xbmcgui.Dialog().select('Add albums to favorites? (i8n)', [
           node.get_label() for node in nodes                              
        ])
        if ret == -1:
            return False
        album_ids = ','.join([node.id for node in nodes])
        if not self.add_albums(album_ids):
            notifyH(heading, 'Cannot add album(s) to favorite')
            return False
        notifyH(heading, 'Album(s) added to favorite')
        return True
    
    def list_albums(self, qnt, qid):
        album_ids = {}
        nodes = []
        if qnt & Flag.PRODUCT == Flag.PRODUCT:
            node = Node_product(None, {'nid': qid})
            node.pre_build_down(None, None, None, None)
            album_ids[str(node.id)] = 1
            nodes.append(node)
        elif qnt & Flag.TRACK == Flag.TRACK:
            render = getRenderer(qnt, self.parameters)
            render.depth = 1
            render.whiteFlag = Flag.TRACK
            render.blackFlag = Flag.NONE
            render.asList = True
            render.run()
            if len(render.nodes) > 0:
                node = Node_product(None)
                node.data = render.nodes[0].data['album']
                album_ids[str(node.id)] = 1
                nodes.append(node)
        else:
            render = getRenderer(qnt, self.parameters)
            render.depth = -1
            render.whiteFlag = Flag.PRODUCT
            render.blackFlag = Flag.STOPBUILD & Flag.TRACK
            render.asList = True
            render.run()
            for node in render.nodes:
                if node.type & Flag.PRODUCT: 
                    if not str(node.id) in album_ids:
                        album_ids[str(node.id)] = 1
                        nodes.append(node)
                if node.type & Flag.TRACK:
                    render = getRenderer(qnt, self.parameters)
                    render.depth = 1
                    render.whiteFlag = Flag.TRACK
                    render.blackFlag = Flag.NONE
                    render.asList = True
                    render.run()
                    if len(render.nodes) > 0:
                        newnode = Node_product(None)
                        newnode.data = render.nodes[0].data['album']
                        if not str(newnode.id) in album_ids:
                            nodes.append(newnode)
                            album_ids[str(newnode.id)] = 1
        return nodes
    
    def add_albums(self, album_ids):
        ret = api.favorite_create(album_ids=album_ids)
        if not ret:
            print "Cannot add album_ids to favorite"
            return False
        qobuz.registry.delete(name='user-favorites')
        print "albums_ids added to favorite"
        return True
    
    def gui_add_tracks(self):
        heading = 'Qobuz Favorites (i8n)'
        qnt = int(self.get_parameter('qnt'))
        qid = self.get_parameter('qid')
        nodes = self.list_tracks(qnt, qid)
        if len(nodes) == 0:
            notifyH(heading, 'Nothing to add')
            return False
        ret = xbmcgui.Dialog().select('Add this tracks to favorites? (i8n)', [
           node.get_label() for node in nodes                              
        ])
        if ret == -1:
            return False
        track_ids = ','.join([str(node.id) for node in nodes])
        print 'TrackIDS %s' % (track_ids)
#        return True
        if not self.add_tracks(track_ids):
            notifyH(heading, 'Cannot add track(s) to favorite')
            return False
        notifyH(heading, 'Track(s) added to favorite')
        return True
    
    def list_tracks(self, qnt, qid):
        track_ids = {}
        nodes = []
        if qnt & Flag.TRACK == Flag.TRACK:
            print "Adding one track :)"
            node = Node_track(None, {'nid': qid})
            node.pre_build_down(None, None, None, Flag.NONE)
            track_ids[str(node.id)] = 1
            nodes.append(node)
        else:
            render = getRenderer(qnt, self.parameters)
            render.depth = -1
            render.whiteFlag = Flag.TRACK
#            render.blackFlag = Flag.STOPBUILD & Flag.TRACK & Flag.PRODUCT
            render.asList = True
            render.run()
            for node in render.nodes:
                if not str(node.id) in track_ids:
                    nodes.append(node)
                    track_ids[str(node.id)] = 1
        return nodes
    
    def add_tracks(self, track_ids):
        ret = api.favorite_create(track_ids=track_ids)
        if not ret:
            print "Cannot add album_ids to favorite"
            return False
        qobuz.registry.delete(name='user-favorites')
        print "albums_ids added to favorite"
        return True
    
    def remove(self):
        log(self, "Removing favorite: " + repr(self.id))
        if not api.favorite_delete(track_ids=str(self.id)):
            return False
        qobuz.registry.delete(name='user-favorites')
        return True
