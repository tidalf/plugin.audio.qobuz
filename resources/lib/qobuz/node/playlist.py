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
from constants import Mode
from flag import NodeFlag as Flag
from node import Node
from product import Node_product
from debug import info, warn
from exception import QobuzXbmcError
from gui.util import notifyH, notify, color, lang, getImage, runPlugin, containerRefresh

'''
    NODE PLAYLIST
'''
from track import Node_track


class Node_playlist(Node):

    def __init__(self, parent=None, parameters=None, progress=None):
        super(Node_playlist, self).__init__(parent, parameters)
        self.type = Flag.NODE | Flag.PLAYLIST
        self.current_playlist_id = None
        self.b_is_current = False
        self.is_my_playlist = False
        self.label = ""
        self.label2 = ""
        self.url = None
        self.is_folder = True
        self.packby = ''
        if self.packby == 'album':
            self.content_type = 'albums'
        else:
            self.content_type = 'songs'

    def get_label(self):
        return self.get_name()

    def set_is_my_playlist(self, b):
        self.is_my_playlist = b

    def set_is_current(self, b):
        self.b_is_current = b

    def is_current(self):
        return self.b_is_current

    def _build_down(self, xbmc_directory, lvl, flag=None):
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        nid = self.id or self.get_parameter('nid')
        info(self, "Build-down playlist")
        data = qobuz.registry.get(
            name='user-playlist', id=nid, offset=offset, limit=limit)
        if not data:
            warn(self, "Build-down: Cannot fetch playlist data")
            return False
        albumseen = {}
        for jtrack in data['data']['tracks']['items']:
            node = None
            if self.packby == 'album':
                jalbum = jtrack['album']
                if jalbum['id'] in albumseen:
                    continue
                keys = ['artist', 'interpreter', 'composer']
                for k in keys:
                    if k in jtrack:
                        jalbum[k] = jtrack[k]
                if 'image' in jtrack:
                    jalbum['image'] = jtrack['image']
                node = Node_product()
                cdata = qobuz.registry.get(
                    name='product', id=jalbum['id'], noRemote=True)
                node.data = cdata or jalbum
                albumseen[jalbum['id']] = node
            else:
                node = Node_track()
                node.data = jtrack
            self.add_child(node)
        self.add_pagination(data['data'])

    def get_name(self):
        name = self.get_property('name')
        return name

    def get_owner(self):
        return self.get_property(('owner', 'name'))

    def get_owner_id(self):
        return self.get_property(('owner', 'id'))

    def get_description(self):
        return self.get_property('description')

    def make_XbmcListItem(self):
        colorItem = qobuz.addon.getSetting('color_item')
        colorPl = qobuz.addon.getSetting('color_item_playlist')
        label = self.get_name()
        image = self.get_image()
        owner = self.get_owner()
        url = self.make_url()
        if self.b_is_current:
            label = ''.join(('-o] ', color(colorItem, label), ' [o-'))
        if not self.is_my_playlist:
            label = color(colorItem, owner) + ' - ' + self.get_name()
        label = color(colorPl, label)
        item = xbmcgui.ListItem(label,
                                owner,
                                image,
                                image,
                                url)
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        item.setPath(url)
        menuItems = []
        self.attach_context_menu(item, menuItems)
        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems, replaceItems=False)
        return item

    def attach_context_menu(self, item, menuItems=[]):
        login = qobuz.addon.getSetting('username')
        isOwner = True
        if login != self.get_property(('owner', 'name')):
            isOwner = False
        colorItem = qobuz.addon.getSetting('color_item')
        colorWarn = qobuz.addon.getSetting('color_item_caution')
        label = self.get_label()

        if isOwner:
            url = self.make_url(type=Flag.PLAYLIST, nm='set_as_current')
            menuItems.append((
                color(colorItem, lang(39007) + ': ') + label, runPlugin(url)))

            url = self.make_url(type=Flag.PLAYLIST, nm='rename')
            menuItems.append((
                color(colorItem, lang(39009) + ': ') + label, runPlugin(url)))

        else:
            url = self.make_url(type=Flag.PLAYLIST, nm='subscribe')
            menuItems.append((
                color(colorItem, lang(39012) + ': ') + label, runPlugin(url)))

        url = self.make_url(type=Flag.PLAYLIST, nm='create')
        menuItems.append((color(colorItem, lang(39008)), runPlugin(url)))

        url = self.make_url(type=Flag.PLAYLIST, nm='remove')
        menuItems.append(
            (color(colorWarn, lang(39010) + ': ') + label, runPlugin(url)))

        ''' Calling base class '''
        super(Node_playlist, self).attach_context_menu(item, menuItems)

    def remove_tracks(self, tracks_id):
        import qobuz
        import xbmc
        info(self, "Removing tracks: " + tracks_id)
        result = qobuz.api.playlist_deleteTracks(
            playlist_id=self.id, playlist_track_ids=tracks_id)
        if not result:
            warn(self, "Cannot remove tracks from playlist: " + str(self.id))
            notifyH('Qobuz Playlist / Remove track', "Fail to remove track")
            return False
        info(self, "Tracks removed from playlist: " + str(self.id))
        qobuz.registry.delete(name='user-playlist', id=self.id)
        xbmc.executebuiltin('Container.Refresh')
        return True

    def add_to_current_playlist(self):
            from gui.directory import Directory
            from renderer.xbmc import Xbmc_renderer as renderer
            cid = qobuz.registry.get(
                name='user-current-playlist-id', noRemote=True)
            if cid:
                cid = cid['data']
            if not cid:
                warn(self, 'no current playlist id')
                notify(29000, 29001, getImage('icon-error-256'))
                return False
            nt = None
            try:
                nt = int(self.get_parameter('nt'))
            except:
                warn(self, "No node type...abort")
                return False
            ID = None
            try:
                ID = self.get_parameter('nid')
            except:
                pass
            depth = -1
            try:
                depth = int(self.get_parameter('depth'))
            except:
                pass
            view_filter = 0
            try:
                view_filter = int(self.get_parameter('view-filter'))
            except:
                pass
            render = renderer(nt, ID)
            render.set_depth(depth)
            render.set_filter(view_filter)
            render.set_root_node()
            Dir = Directory(render.root, qobuz.boot.handle, True)
            flags = Flag.TRACK | Flag.DONTFETCHTRACK
            if render.root.type & Flag.TRACK:
                flags = Flag.TRACK
            ret = render.root.build_down(Dir, depth, flags)
            if not ret:
                Dir.end_of_directory()
                return False
            track_ids = []
            if len(Dir.nodes) < 1:
                warn(self, "No track to add to current playlist")
                Dir.end_of_directory()
                return False
            for node in Dir.nodes:
                track_ids.append(str(node.id))
            str_tracks = ','.join(track_ids)
            ret = qobuz.api.playlist_addTracks(
                playlist_id=str(cid), track_ids=str_tracks)
            if ret:
                qobuz.registry.delete(name='user-playlist', id=cid)
            Dir.end_of_directory()
            return True

    def add_as_new_playlist(self):
        from gui.directory import Directory
        from user_playlists import Node_user_playlists
        from renderer.xbmc import Xbmc_renderer as renderer
        nt = None
        try:
            nt = int(self.get_parameter('nt'))
        except:
            warn(self, "No node type...abort")
            return False
        ID = None
        try:
            ID = self.get_parameter('nid')
        except:
            pass
        depth = -1
        try:
            depth = int(self.get_parameter('depth'))
        except:
            pass
        view_filter = 0
        try:
            view_filter = int(self.get_parameter('view-filter'))
        except:
            pass
        render = renderer(nt, ID)
        render.set_depth(depth)
        render.set_filter(view_filter)
        render.set_root_node()
        Dir = Directory(render.root, qobuz.boot.handle, True)
        flags = Flag.TRACK | Flag.DONTFETCHTRACK
        if render.root.type & Flag.TRACK:
            flags = Flag.TRACK
        ret = render.root.build_down(Dir, depth, flags)
        if not ret:
            Dir.end_of_directory()
            warn(self, "Nothing to add as new playlist")
            return False
        info(self, "CREATE PLAYLIST: " + repr(render.root.get_label()))
        userplaylists = Node_user_playlists()
        nid = userplaylists.create_playlist(render.root.get_label())
        if not nid:
            warn(self, "Cannot create playlist...")
            Dir.end_of_directory()
            return False
        trackids = []
        if len(Dir.nodes) < 1:
            warn(self, "No track to add to current playlist")
            Dir.end_of_directory()
            qobuz.registry.set(
                name='user-current-playlist-id', value=nid, noRemote=True)
            qobuz.registry.delete(name='user-playlist', id=nid)
            qobuz.registry.deleet(name='user-playlists')
            return False
        for node in Dir.nodes:
            trackids.append(str(node.id))
        strtracks = ','.join(trackids)
        ret = qobuz.api.playlist_addTracks(
            playlist_id=nid, track_ids=strtracks)
        if ret:
            qobuz.registry.delete(name='user-playlist', id=nid)
            qobuz.registry.deleet(name='user-playlists')
            qobuz.registry.set(
                name='user-current-playlist-id', value=nid, noRemote=True)
        Dir.end_of_directory()
        return True

    def set_as_current(self):
        from gui.util import containerRefresh
        if not self.id:
            raise QobuzXbmcError(who=self, what='node_without_id')
        qobuz.registry.set(
            name='user-current-playlist-id', id=0, value=self.id)
        containerRefresh()
        return True

    '''
        Rename playlist
    '''
    def rename(self):
        from gui.util import Keyboard, containerRefresh
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        info(self, "renaming playlist: " + str(self.id))
        playlist = qobuz.registry.get(
            name='user-playlist', id=self.id, offset=offset, limit=limit)
        currentname = playlist['data']['name']
        k = Keyboard(currentname, lang(30078))
        k.doModal()
        if not k.isConfirmed():
            return False
        newname = k.getText()
        newname = newname.strip()
        print "Name: " + repr(newname)
        if newname == currentname:
            return True
        res = qobuz.api.playlist_update(playlist_id=self.id, name=newname)
        if not res:
            containerRefresh()
            return False
        else:
            qobuz.registry.delete(name='user-playlist', id=self.id)
            qobuz.registry.delete_by_name(name='^user-playlists-.*\.dat$')
            containerRefresh()
            notifyH(lang(30078), (u"%s: %s") % (lang(39009), currentname))
        return True

    def create(self):
        from gui.util import containerRefresh
        query = self.get_parameter('query')
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
        self.set_as_current()
        qobuz.registry.delete_by_name(name='^user-playlists-.*\.dat$')
        containerRefresh()
        return ret['id']

    '''
        Remove playlist
    '''
    def remove(self):
        import xbmcgui
        import xbmc
        import pprint
        ID = self.id
        login = qobuz.addon.getSetting('username')
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(
            name='user-playlist', id=ID, offset=offset, limit=limit)['data']
        print pprint.pformat(data)
        name = ''
        if 'name' in data:
            name = data['name']
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
            notifyH('Qobuz remove playlist (i8n)', 'Cannot remove playlist ' +
                    name, getImage('icon-error-256'))
            return False
        qobuz.registry.delete(
            name='user-playlists', offset=offset, limit=limit)
        notifyH('Qobuz remove playlist (i8n)', 'Playlist ' + name + ' removed')
        containerRefresh()
        return True

    def subscribe(self):
        ID = self.id
        if qobuz.api.playlist_subscribe(playlist_id=ID):
            from gui.util import notifyH, isFreeAccount, lang
            notifyH("Qobuz", "(i8n) playlist subscribed")
            qobuz.registry.delete_by_name('^user-playlists.*\.dat$')
            return True
        else:
            return False
