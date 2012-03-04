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

import os
import sys
import urllib

import xbmcplugin
import xbmcgui
import xbmc

from constants import *
from debug import *
from debug import __debugging__

import qobuz

'''
    CLASS QobuzGUI
'''
class QobuzGUI:

    def __init__( self):
        pass
#        self.setPluginFanArt()
#        self.setPluginCategory()
#        self.sort_enabled = True
#        self.content_type = None
#        xbmc.enableNavSounds(False)
#        
#
#    def set_sort_enabled(self, b):
#        self.sort_enabled = b
#        
#    def set_content_type(self, ctx):
#        contexts = ['files', 'songs', 'artists', 'albums', 'movies', 'tvshows', 'episodes', 'musicvideos']
#        if ctx not in contexts:
#            warn(self, "Invalid content type")
#            return False
#        self.content_type = ctx
#        return True
#    
#    def set_view_mode(self, view):
#        viewmode = {'list': 50, 
#                    'icons': 52, 
#                    'biglist': 51,
#                    'thumbnails': 500,
#                    'mediainfo': 506 }
#        if view not in viewmode:
#            warn(self, "Try to set invalid view mode: " + str(view))
#            view = 'list'
#        s = 'Container.setViewMode(%i)' % (int(viewmode[view]))
#        xbmc.executebuiltin(s)
#        return True
#    
#    '''
#    Must be called at the end for folder to be displayed
#    '''
#    def endOfDirectory(self, succeeded = True):
#        return xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=succeeded, updateListing=False, cacheToDisc=True)
#    
#    '''
#        SHOW Notification (HUMAN ONE / NO i8n)
#    '''
#    def showNotificationH(self, title, text, image = None):
#        if not image:
#            image = qobuz.image.access.get('qobuzIcon')
#        title = str(title) 
#        text = str(text)
#        s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (title, text, 2000, image) 
#        try:
#            xbmc.executebuiltin(s)
#        except:
#            warn(self, "Notification failure")
#            
#    '''
#        SHOW Notification
#    '''
#    def showNotification(self, title, text, image = None):
#        if not image:
#            image = qobuz.image.access.get('qobuzIcon')
#        l = qobuz.lang
#        s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (l(title), l(text), 2000, image) 
#        xbmc.executebuiltin(s)
#
#    def notification(self, title, text, image = None):
#        self.showNotification(title, text, image)
#        
#    '''
#        SET FanArt
#    '''
#    def setPluginFanArt(self, fanart = 'fanart'):
#        xbmcplugin.setPluginFanart(qobuz.boot.handle,  qobuz.image.access.get('fanArt'), '0xFFFFFFFF', '0xFFFF3300', '0xFF000000')
#      
#    def setPluginCategory(self):
#        xbmcplugin.setPluginCategory(handle=qobuz.boot.handle, category="Music Streaming")
#
#    '''
#        SET Content
#    '''        
#    def setContent(self):
#        debug(self, "Set content: " + self.content_type)
#        xbmcplugin.setContent(handle=qobuz.boot.handle, content=self.content_type)
#
    def show_login_failure(self):
        __language__ = qobuz.lang
        dialog = xbmcgui.Dialog()
        if dialog.yesno(__language__(30008), __language__(30034), __language__(30040)):
            qobuz.addon.openSettings()
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False, updateListing=True, cacheToDisc=False)
            return self.boot.dispatch()
        else:        
            xbmc.executebuiltin('ActivateWindow(home)')
            return False
#    '''
#        Get keyboard input
#    '''
#    def _get_keyboard(self, default="", heading="", hidden=False):
#        kb = xbmc.Keyboard(default, heading, hidden)
#        kb.doModal()
#        if (kb.isConfirmed()):
#            return unicode(kb.getText(), "utf-8")
#        return ''
#    
#    def setContextMenu(self, item, context = 'all'):
#        import urllib
#        color = qobuz.addon.getSetting('color_ctxitem')
#        menuItems = []
##        ''' MANAGE PLAYLIST '''
#        if __debugging__:
#            manageplaylist=sys.argv[0]+"?mode="+str(MODE_MANAGE_PLAYLIST)
#            menuItems.append((qobuz.utils.color(color, qobuz.lang(31010) + ' (Qobuz 2.x - dev)'), "XBMC.RunPlugin("+manageplaylist+")"))
#        ''' ERASE CACHE '''
#        erasecache=sys.argv[0]+"?mode="+str(MODE_ERASE_CACHE)
#        menuItems.append((qobuz.utils.color(color, qobuz.lang(31009)), "XBMC.RunPlugin("+erasecache+")"))
#        
#        url = sys.argv[0] + "?mode="+str(MODE_LIBRARY_SCAN) + "&url=" + urllib.quote(sys.argv[2]) 
#        menuItems.append((qobuz.utils.color(color, "Scan"), "XBMC.RunPlugin("+url+")"))                                                             
#        
##        ''' Test Node '''
##        cmd=sys.argv[0]+"?mode="+str(MODE_TEST)
##        menuItems.append(('Test NODE', "XBMC.RunPlugin("+cmd+")"))
##        
##        ''' Test Node '''
##        cmd=sys.argv[0]+"?mode="+str(MODE_NODE)+"&nt=4096"
##        menuItems.append(('Test Node Playlist', "XBMC.RunPlugin("+cmd+")"))
#        item.addContextMenuItems(menuItems, replaceItems=False)
#    
#    '''
#        Add directory
#    '''
#    def _add_dir(self, name, url, mode, iconimage, id, items=0):
#        __language__= qobuz.lang
#        if url == '':
#            u=qobuz.boot.build_url(mode, id)
#        else:
#            u = url
#        dir=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
#        dir.setInfo( type="Music", infoLabels={ "title": name.encode('utf8', 'ignore') } )
#        dir.setProperty('fanart_image', qobuz.image.access.get('fanArt'))
#        dir.setPath(u)
#        self.setContextMenu(dir)
#        dir.setProperty('path', u)
#
#        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=dir,isFolder=True, totalItems=items)
#    
#        '''
#        Add to directory
#    '''
#    def add_to_directory(self, list, context = 'playlist'):
#        n = len(list)
#        if n < 1:
#            self.showNotificationH("Qobuz", "Empty directory")
#            return False
#        self.setContent()
#        h = qobuz.boot.handle
#        if self.sort_enabled:
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_ALBUM)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_ALBUM_IGNORE_THE)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TRACKNUM)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_ARTIST)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_EPISODE)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_FILE)
#            xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
#        xbmcplugin.addDirectoryItems(handle=h, items=list, totalItems=100)
#        return True
#
#    '''
#        Top-level menu
#    '''
#    def showCategories(self):
#        self.set_content_type('files')
#        self.set_view_mode('icons')
#        i = qobuz.image.access
#        __language__ = qobuz.lang
#        if qobuz.addon.getSetting('search_enabled') == 'true':
#            self._add_dir(__language__(30013), '', MODE_SEARCH_SONGS, i.get('song'), 0)
#            self._add_dir(__language__(30014), '', MODE_SEARCH_ALBUMS, i.get('album'), 0)
#            self._add_dir(__language__(30015), '', MODE_SEARCH_ARTISTS, i.get('artist'), 0)
#        else: info(self, "Search is disabled!")
#        self._add_dir(__language__(30082), '', MODE_SHOW_RECOS, i.get('playlist'), 0)
#        self._add_dir(__language__(30101), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=new-releases', MODE_SHOW_RECO_T, i.get('playlist'), 0)
#        self._add_dir(__language__(30100), '', MODE_SHOW_PURCHASES, i.get('album'), 0)
#        if (qobuz.api.userid != 0):
#            self._add_dir(__language__(30019), '', MODE_USERPLAYLISTS, i.get('usersplaylists'), 0)
#        if __debugging__:
#            self._add_dir("qobuz 2.x (dev)", sys.argv[0]+"?mode="+str(MODE_NODE)+"&nt=16384", MODE_NODE, i.get('album'), 0)
#        return True
#
#    """
#        SEARCH for songs
#    """
#    def searchSongs(self):
#        self.set_content_type('songs')
#        __language__ = qobuz.lang
#        query = self._get_keyboard(default="",heading=__language__(30020))
#        query = query.strip()
#        if (query != ''):
#            s = qobuz.core.getQobuzSearchTracks()
#            s.search(query, qobuz.addon.getSetting('songsearchlimit'))
#            list = s.get_items()
#            if len(list) < 1:
#                self.showNotification(36000, 35001)
#                self.searchSongs()
#                return False
#            self.add_to_directory(list)
#            return True
#        else:
#            return self.showCategories()
#  
#    """
#        SEARCH for Albums
#    """
#    def searchAlbums(self):
#        self.set_content_type('albums')
#        __language__ = qobuz.lang
#        query = self._get_keyboard(default="",heading=__language__(30022))
#        query = query.strip()
#        if (query != ''):
#            s = qobuz.core.getQobuzSearchAlbums()
#            s.search(query, qobuz.addon.getSetting('albumsearchlimit'))
#            list = s.get_items()
#            if len(list) < 1:
#                self.showNotification(36000, 35002)
#                self.searchAlbums()
#                return False
#            self.add_to_directory(list)
#            return True
#        else:
#            return self.showCategories()
#
#    """
#        SEARCH for Artists
#    """
#    def searchArtists(self):
#        self.set_content_type('artists')
#        __language__ = qobuz.lang
#        query = self._get_keyboard(default="",heading=__language__(30024))
#        query = query.strip()
#        if (query != ''):
#            s = qobuz.core.getQobuzSearchArtists()
#            s.search(query, qobuz.addon.getSetting('artistsearchlimit'))
#            list = s.get_items()
#            if len(list) < 1:
#                self.showNotification(36000, 35003)
#                self.searchArtists()
#                return False
#            self.add_to_directory(list)
#            return True
#        else:
#            return self.showCategories()
#
#    """
#      Show Recommendations 
#    """
#    def showRecommendations(self, type, genre_id):
#        self.set_content_type('files')
#        if (genre_id != ''):
#            r = qobuz.core.getRecommandation(genre_id, type)
#            list = r.get_items()
#            if len(list) < 1:
#                self.showNotification(36000, 36001)
#                return False
#            self.add_to_directory(list)
#            return True
#        else:
#            self.showNotificationH('Qobuz', 'No genre_id for recommandation')
#            return self.showCategories()
#        
#
#    '''
#        SHOW Purchases
#    '''
#    def showPurchases(self):
#        self.set_content_type('albums')
#        r = qobuz.core.getPurchases()
#        list = r.get_items()
#        if len(list) < 1:
#            self.showNotification(36000, 36001)
#            return False
#        self.add_to_directory(list)
#        return True
#    
#    '''
#        SHOW Recommandations Types
#    '''
#    def showRecommendationsTypes(self):
#        self.set_content_type('files')
#        __language__ = qobuz.lang
#        i = qobuz.image.access
#        self._add_dir(__language__(30083), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=press-awards','', i.get('song'), 0)
#        self._add_dir(__language__(30084), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=new-releases','', i.get('song'), 0)
#        self._add_dir(__language__(30085), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=best-sellers','', i.get('song'), 0)
#        self._add_dir(__language__(30086), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=editor-picks','', i.get('song'), 0)
#        return True
#
#    '''
#        SHOW Recommandations Genre
#    '''
#    def showRecommendationsGenres(self, type):
#        self.set_content_type('files')
#        self.set_view_mode('thumbnails')
#        import time
#        import math
#        ti = '?t='+str(int(time.time()))
#        __language__ = qobuz.lang
#        i = qobuz.image
#        qobuzIcon = qobuz.image.access.get('qobuzIcon')
#        def gi(id):
#            image = qobuz.image.cache.get(type + str(id))
#            if not image: return qobuzIcon
#            return image
#            
#        self._add_dir(__language__(30087), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=112',MODE_SHOW_RECO_T_G, gi(112), 10)
#        self._add_dir(__language__(30088), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=64',MODE_SHOW_RECO_T_G, gi(64), 10)
#        self._add_dir(__language__(30089), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=80',MODE_SHOW_RECO_T_G, gi(80), 10)
#        self._add_dir(__language__(30090), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=6',MODE_SHOW_RECO_T_G,  gi(6), 10)
#        self._add_dir(__language__(30091), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=127',MODE_SHOW_RECO_T_G, gi(127), 10)
#        self._add_dir(__language__(30092), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=94',MODE_SHOW_RECO_T_G, gi(94), 10)
#        self._add_dir(__language__(30093), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=2',MODE_SHOW_RECO_T_G, gi(2), 10)
#        self._add_dir(__language__(30094), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=91',MODE_SHOW_RECO_T_G, gi(91), 10)
#        self._add_dir(__language__(30095), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=10',MODE_SHOW_RECO_T_G, gi(10), 10)
#        self._add_dir(__language__(30097), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=123',MODE_SHOW_RECO_T_G, gi(123), 10)
#        self._add_dir(__language__(30096), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=null',MODE_SHOW_RECO_T_G, qobuzIcon, 10)
#        return True
#        
#    
#    '''
#        SHOW User Playlists
#    '''
#    def showUserPlaylists(self):
#        self.set_content_type('files')
#        self.set_view_mode('thumbnails')
#        user_playlists = qobuz.core.getUserPlaylists()
#        list = user_playlists.get_items()
#        if len(list) < 1:
#            self.showNotification(36000, 36001)
#            return False
#        self.add_to_directory(list)
#        return True
#    
#    '''
#        SHOW Playlist
#    '''
#    def showPlaylist(self, id):
#        self.set_content_type('songs')
#        self.set_view_mode('thumbnails')
#        userid = qobuz.api.userid
#        if (userid != 0):
#            myplaylist = qobuz.core.getPlaylist(id)
#            list = myplaylist.get_items()
#            if len(list) < 1:
#                self.showNotification(36000, 36001)
#                return False
#            self.add_to_directory(list)
#            return True
#        else:
#            dialog = xbmcgui.Dialog()
#            dialog.ok(__language__(30008), __language__(30034), __language__(30040))
#        return False
#    
#    '''
#        SHOW Product
#    '''
#    def showProduct (self, id, context_type = "playlist"):
#        self.set_content_type('songs')
#        album = qobuz.core.getProduct(id,context_type)
#        list = album.get_items()
#        if len(list) < 1:
#            self.showNotification(36000, 36001)
#            return False
#        self.add_to_directory(list)
#        return True
#
#    '''
#        SHOW Artsit
#    '''
#    def showArtist (self, id):
#        self.set_content_type('artists')
#        album = qobuz.core.getProductsFromArtist()
#        album.search_by_artist(id)
#        if album.length() < 1:
#            self.showNotification(30008, 30033)
#            return False
#        list = album.get_items_by_artist()
#        self.add_to_directory(list)
#        return True
#
#    def create_playlist(self):
#        from utils.cache import cache_manager
#        from data.userplaylists import QobuzUserPlaylistsXbmc
#        query = self._get_keyboard(default="",heading='Create playlist')
#        query = query.strip()
#        #info(self, "Query: " + repr(query))
#        if query != '':
#            print "Creating playlist: " + query
#        ret = qobuz.api.playlist_create(query, '', '', '', 'off', 'off')
#        if not ret:
#            warn(self, "Cannot create playlist name '"+ query +"'")
#            return False
#        print ret
#        userplaylists = QobuzUserPlaylistsXbmc()
#        cm = cache_manager()
#        cm.delete(userplaylists.get_cache_path())
#        self.set_current_playlist(ret['playlist']['id'])
#        info(self, "Container refreshing neeeded!")
#        xbmc.executebuiltin('Container.Refresh')
#            
#    def set_current_playlist(self, id):
#        log(self, "Set current playlist: " + str(id))
#        from data.current_playlist import Cache_current_playlist
#        cp = Cache_current_playlist()
#        if cp.get_id() == id:
#            log(self, "Playlist already selected... do nothing")
#            return True
#        cp.set_id(id)
#        cp.save()
#        xbmc.executebuiltin('Container.Refresh')
#        return True
#
#        
#    def rename_playlist(self, id):
#        log(self, "rename playlist: " + str(id))
#        from utils.cache import cache_manager
#        from data.userplaylists import QobuzUserPlaylistsXbmc
#        from data.playlist import QobuzPlaylist
#        from tag.playlist import TagPlaylist
#        cm = cache_manager()
#        info(self, "GUI! rename playlist id: " + str(id))
#        playlist = QobuzPlaylist(id)
#        tag = TagPlaylist(playlist.fetch_data())
#        current_name = tag.getName()
#        query = self._get_keyboard(default=current_name,heading='Rename playlist')
#        query = query.strip()
#        #info(self, "Query: " + repr(query))
#        if query != '' and query != current_name:
#            #info(self, "Renaming playlist " + current_name + ' to ' + repr(query))
#            res = qobuz.api.playlist_update(id, query, tag.getDescription(), tag.getIsPublic(), tag.getIsCollaborative())
#            if not res:
#                warn("Playlist updating request fail!")
#                return False
#            cm.delete(playlist.get_cache_path())
#            userplaylists = QobuzUserPlaylistsXbmc()
#            cm.delete(userplaylists.get_cache_path())
#            info(self, "Container refreshing neeeded!")
#            xbmc.executebuiltin('Container.Refresh')
#        else:
#            warn(self, "Playlist renaming aborted")
#            # Notify that an we are not renaming item
#            pass
#            
#        
