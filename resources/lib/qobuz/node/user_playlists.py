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
import xbmc

import qobuz
from flag import NodeFlag
from node import Node
from debug import info, warn, error, debug
from gui.util import color, lang, getImage, notifyH, containerRefresh

'''
    NODE USER PLAYLISTS
'''

from playlist import Node_playlist

class Node_user_playlists(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_user_playlists, self).__init__(parent, parameters)
        self.label = lang(30019)
        self.image = getImage('userplaylists')
        self.label2 = 'Keep your current playlist'
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_USERPLAYLISTS
        self.content_type = 'files'
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
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        debug(self, "Build-down: user playlists")
        data = qobuz.registry.get(name='user-playlists', limit=limit, offset=offset)
        if not data:
            warn(self, "Build-down: Cannot fetch user playlists data")
            return False
        cid = qobuz.registry.get(name='user-current-playlist-id', noRemote=True)
        if cid: cid = int(cid['data'])
        for playlist in data['data']['playlists']['items']:
            node = Node_playlist()
            node.data = playlist
            if self.display_product_cover:
                pass
            if (cid and cid == node.id):
                node.set_is_current(True)
            if node.get_owner() == login:
                node.set_is_my_playlist(True)
            self.add_child(node)
        self.add_pagination(data['data'])
        return True

    def set_current_playlist(self, ID):
        qobuz.registry.set(name='user-current-playlist-id', id=0, value=ID)
    
    def subscribe_playlist(self, ID):
        if qobuz.api.playlist_subscribe(playlist_id = ID):
            from gui.util import notifyH, isFreeAccount, lang
            notifyH("Qobuz","(i8n) playlist subscribed")
            qobuz.registry.delete_by_name('^user-playlists.*\.dat$')
            return True
        else: 
            return False
        
    def create_playlist(self, query = None):
        #!TODO: Why we are no more logged ...
        qobuz.registry.get(name='user')
        if not query:
            from gui.util import Keyboard
            k = Keyboard('', 'Create Playlist (i8n)')
            k.doModal()
            if not k.isConfirmed():
                warn(self, 'Creating playlist aborted')
                return None
            query = k.getText()
        ret = qobuz.api.playlist_create(name=query, is_public=False)
        if not ret:
            warn(self, "Cannot create playlist name '" + query + "'")
            return None
        self.set_current_playlist(ret['id'])
        qobuz.registry.delete_by_name(name='^user-playlists-.*\.dat$')
        containerRefresh()
        return ret['id']

    ''' 
        Rename playlist 
    '''
    def rename_playlist(self, ID):
        from gui.util import Keyboard
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        info(self, "renaming playlist: " + str(ID))
        playlist = qobuz.registry.get(name='user-playlist', id=ID, offset=offset, limit=limit)
        currentname = playlist['data']['name'].encode('utf8', 'replace')
        k = Keyboard(currentname, lang(30078))
        k.doModal()
        if not k.isConfirmed():
            return False
        newname = k.getText()
        newname = newname.strip()
        if newname == currentname:
            return True
        res = qobuz.api.playlist_update(playlist_id=ID,name=newname)
        if not res:
#            qobuz.registry.delete(name='user-playlist', id=ID)
#            qobuz.registry.delete_by_name(name='^user-playlists-.*\.dat$')
            containerRefresh()
            return False
        else:
            qobuz.registry.delete(name='user-playlist', id=ID)
            qobuz.registry.delete_by_name(name='^user-playlists-.*\.dat$')
            containerRefresh()
            notifyH(lang(30078), lang(39009) + ': ' + currentname)
        return True
    
    '''
        Remove playlist
    '''
    def remove_playlist(self, ID):
        import xbmcgui, xbmc
        import pprint
        login = qobuz.addon.getSetting('username')
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(name='user-playlist', id=ID, offset=offset, limit=limit)['data']
        print pprint.pformat(data)
        name = ''
        if 'name' in data: name = data['name']
        ok = xbmcgui.Dialog().yesno(lang(39010),
                          lang(30052), 
                          color('FFFF0000', name))
        if not ok:
            info(self, "Deleting playlist aborted...")
            return False
        res = False
        if data['owner']['name'] == login:
            info(self, "Deleting playlist: " + ID)
            res = qobuz.api.playlist_delete(playlist_id=ID)
        else:
            info(self, 'Unsuscribe playlist' + ID)
            res = qobuz.api.playlist_unsubscribe(playlist_id=ID)
        if not res:
            warn(self, "Cannot delete playlist with id " + str(ID))
            notifyH('Qobuz remove playlist (i8n)', 'Cannot remove playlist ' + name, getImage('icon-error-256'))
            return False
        qobuz.registry.delete(name='user-playlists', offset=offset, limit=limit)
        notifyH('Qobuz remove playlist (i8n)', 'Playlist ' + name + ' removed')
        containerRefresh()
        return True
