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
import sys
import random
import pprint

import xbmc

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from debug import info, warn, error, debug


'''
    NODE USER PLAYLISTS
'''

from playlist import Node_playlist

class Node_user_playlists(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_user_playlists, self).__init__(parent, parameters)
        self.label = qobuz.utils.lang(30019)
        #self.image = qobuz.image.access.get('userplaylists')
        self.label2 = 'Keep your current playlist'
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_USERPLAYLISTS
        self.set_content_type('files')
        display_by = self.get_parameter('display-by')
        if not display_by: display_by = 'songs'
        self.set_display_by(display_by)
        display_cover = qobuz.addon.getSetting('userplaylists_display_cover')
        if display_cover == 'true': display_cover = True
        else: display_cover = False
        self.display_product_cover = display_cover


    def set_display_by(self, type):
        vtype = ('product', 'songs')
        if not type in vtype:
            error(self, "Invalid display by: " + type)
        self.display_by = type

    def get_display_by(self):
        return self.display_by

    def _build_down(self, xbmc_directory, lvl, flag = None):
        login = qobuz.addon.getSetting('username')
        debug(self, "Build-down: user playlists")
        data = qobuz.registry.get(name='user-playlists')
        if not data:
            warn(self, "Build-down: Cannot fetch user playlists data")
            return False
        cid = qobuz.registry.get(name='user-current-playlist-id', noRemote=True)
        if cid: cid = int(cid['data'])
        for playlist in data['data']['playlists']['items']:
            node = Node_playlist()
            node.set_data(playlist)
            if self.display_product_cover:
                pass
                #image = qobuz.image.cache.get('playlist-' + str(node.get_id()))
                #if not image: image = self.get_random_image(node)
                #if image: node.image = image
            if (cid and cid == node.get_id()):
                node.set_is_current(True)
            if node.get_owner() == login:
                node.set_is_my_playlist(True)
            self.add_child(node)
        return True

    def get_random_image(self, node):
        node.set_cache()
        node.cache.no_network = True
        newdata = node.cache.fetch_data()
        image = None
        if not newdata: return None
        node.set_data(newdata)
        size = len(newdata['tracks'])
        if size < 1: return None
        r = random.randint(0, len(newdata['tracks']) - 1)
        try: image = newdata["tracks"][r]['album']['image']['large']
        except: warn(self, "Cannot get random image for playlist")
        if not image: return None
        qobuz.image.cache.set("playlist-" + str(node.get_id()), image)
        return image

    def set_current_playlist(self, id):
        qobuz.registry.set(name='user-current-playlist-id', id=0, value=id)
        
    def create_playlist(self, query = None):
        #!TODO: Why we are no more logged ...
        qobuz.registry.get(name='user')
        if not query:
            query = self._get_keyboard(default = "", heading = 'Create playlist')
            query = query.strip()
        ret = qobuz.api.playlist_create(name=query, is_public=False)
        if not ret:
            warn(self, "Cannot create playlist name '" + query + "'")
            return None
        self.set_current_playlist(ret['id'])
        qobuz.registry.delete(name='user-playlists')
        return ret['id']

    ''' 
        Rename playlist 
    '''
    def rename_playlist(self, id):
        info(self, "rename playlist: " + str(id))
        playlist = qobuz.registry.get(name='user-playlist', id=id)
        currentname = playlist['data']['name'].encode('utf8', 'replace')
        newname = self._get_keyboard(default = currentname, heading = qobuz.lang(30078))
        newname = newname.strip().encode('utf8', 'replace')
        if newname == currentname:
            return True
        res = qobuz.api.playlist_update(playlist_id=id,name=newname)
        if res:
            qobuz.registry.delete(name='user-playlist', id=id)
            qobuz.registry.delete(name='user-playlists')
            xbmc.executebuiltin('Container.Refresh')
            return False
        else:
            qobuz.gui.notifyH(qobuz.lang(30078), qobuz.lang(39009) + ': ' + currentname)
        return False
    '''
        Remove playlist
    '''
    def remove_playlist(self, id):
        import xbmcgui, xbmc
        data = qobuz.registry.get(name='user-playlist', id=id)['data']
        name = ''
        if 'name' in data: name = data['name']
        ok = xbmcgui.Dialog().yesno(qobuz.lang(39010),
                          qobuz.lang(30052), 
                          qobuz.utils.color('FFFF0000', name))
        if not ok:
            info(self, "Deleting playlist aborted...")
            return False

        info(self, "Deleting playlist: " + id)
        res = qobuz.api.playlist_delete(playlist_id=id)
        if not res:
            warn(self, "Cannot delete playlist with id " + str(id))
            return False
        qobuz.registry.delete(name='user-playlists')
        return True
