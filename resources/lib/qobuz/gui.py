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
from debug import info, warn, log

import qobuz
'''
    CLASS QobuzGUI
'''
class QobuzGUI:

    def __init__( self):
        self.setPluginFanArt()
        

    '''
    Must be called at the end for folder to be displayed
    '''
    def endOfDirectory(self):
        MODE = qobuz.boot.MODE
        ''' SEARCH '''
        if MODE > 30: 
            return xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=False, cacheToDisc=False)
        elif MODE == MODE_SHOW_RECO_T_G:
            return xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=False, cacheToDisc=False)
        else:
            return xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=False, cacheToDisc=True)
    
    '''
        SHOW Notification (HUMAN ONE / NO i8n)
    '''
    def showNotificationH(self, title, text, image = 'qobuzIcon'):
        title = str(title) 
        text = str(text)
        s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (title, text, 2000, qobuz.image.access.get(image)) 
        try:
            xbmc.executebuiltin(s)
        except:
            warn(self, "Notification failure")
            
    '''
        SHOW Notification
    '''
    def showNotification(self, title, text, image = 'qobuzIcon'):
        l = qobuz.lang
        s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (l(title), l(text), 2000, qobuz.image.access.get(image)) 
        xbmc.executebuiltin(s)

    '''
        SET FanArt
    '''
    def setPluginFanArt(self, fanart = 'fanart'):
        xbmcplugin.setPluginFanart(qobuz.boot.handle,  qobuz.image.access.get('fanArt'), '0x00000000')
      
    '''
        SET Content
    '''
    def setContent(self, content):
        '''
        *Note, You can use the above as keywords for arguments.
        content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
        http://xbmc.sourceforge.net/python-docs/xbmcplugin.html
        '''
        xbmcplugin.setContent(qobuz.boot.handle, content)

    '''
        MUST BE REMOVED ?
#    '''  
#    def addDirectoryItem(self, u, item, bFolder, len):
#        h = self.Bootstrap.__handle__
#        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
#        xbmcplugin.addDirectoryItem(handle=h, 
#                                    url=u, listitem=item, isFolder=bFolder, 
#                                    totalItems=len)

    def showLoginFailure(self):
        __language__ = qobuz.lang
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30008), __language__(30034), __language__(30040))
        
    '''
        Top-level menu
    '''
    def showCategories(self):
        i = qobuz.image.access
        __language__ = qobuz.lang
        if qobuz.addon.getSetting('search_enabled') == 'true':
            self._add_dir(__language__(30013), '', MODE_SEARCH_SONGS, i.get('song'), 0)
            self._add_dir(__language__(30014), '', MODE_SEARCH_ALBUMS, i.get('album'), 0)
            self._add_dir(__language__(30015), '', MODE_SEARCH_ARTISTS, i.get('artist'), 0)
        else: info(self, "Search is disabled!")
        self._add_dir(__language__(30082), '', MODE_SHOW_RECOS, i.get('playlist'), 0)
        self._add_dir(__language__(30101), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=new-releases', MODE_SHOW_RECO_T, i.get('playlist'), 0)
        self._add_dir(__language__(30100), '', MODE_SHOW_PURCHASES, i.get('album'), 0)
        if (qobuz.api.userid != 0):
            self._add_dir(__language__(30019), '', MODE_USERPLAYLISTS, i.get('usersplaylists'), 0)
        self.setContent('albums')
        

    """
        SEARCH for songs
    """
    def searchSongs(self):
        __language__ = qobuz.lang
        query = self._get_keyboard(default="",heading=__language__(30020))
        query = query.strip()
        if (query != ''):
            s = qobuz.core.getQobuzSearchTracks()
            s.search(query, qobuz.addon.getSetting('songsearchlimit'))
            list = s.get_items()
            if s.length() < 1:
                self.searchSongs()
                return
            self.add_to_directory(list)
        else:
            self.showCategories()
  
    """
        SEARCH for Albums
    """
    def searchAlbums(self):
        __language__ = qobuz.lang
        query = self._get_keyboard(default="",heading=__language__(30022))
        query = query.strip()
        if (query != ''):
            s = qobuz.core.getQobuzSearchAlbums()
            s.search(query, qobuz.addon.getSetting('albumsearchlimit'))
            if s.length() < 1:
                self.showNotification(30008, 30021)
                self.searchAlbums()
                return
            list = s.get_items()
            self.add_to_directory(list)
        else:
            self.showCategories()

    """
        SEARCH for Artists
    """
    def searchArtists(self):
        __language__ = qobuz.lang
        query = self._get_keyboard(default="",heading=__language__(30024))
        query = query.strip()
        if (query != ''):
            s = qobuz.core.getQobuzSearchArtists()
            s.search(query, qobuz.addon.getSetting('artistsearchlimit'))
            if s.length() < 1:
                self.showNotification(30008, 30021)
                self.searchAlbums()
                return
            list = s.get_items()
            self.add_to_directory(list)
        else:
            self.showCategories()

    """
      Show Recommendations 
    """
    def showRecommendations(self, type, genre_id):
        if (genre_id != ''):
            r = qobuz.core.getRecommandation(genre_id, type)
            list = r.get_items()
            self.add_to_directory(list)
        else:
            self.showNotificationH('Qobuz', 'No genre_id for recommandation')
            self.showCategories()

    '''
        SHOW Purchases
    '''
    def showPurchases(self):
        r = qobuz.core.getPurchases()
        list = r.get_items()
        self.add_to_directory(list)

    '''
        SHOW Recommandations Types
    '''
    def showRecommendationsTypes(self):
        __language__ = qobuz.lang
        i = qobuz.image.access
        #xbmcplugin.setPluginFanart(int(sys.argv[1]), i.get('fanart'))
        self._add_dir(__language__(30083), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=press-awards','', i.get('song'), 0)
        self._add_dir(__language__(30084), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=new-releases','', i.get('song'), 0)
        self._add_dir(__language__(30085), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=best-sellers','', i.get('song'), 0)
        self._add_dir(__language__(30086), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=editor-picks','', i.get('song'), 0)
        self.setContent('songs')

    '''
        SHOW Recommandations Genre
    '''
    def showRecommendationsGenres(self, type):
        import time
        import math
        ti = '?t='+str(int(time.time()))
        __language__ = qobuz.lang
        i = qobuz.image
        self._add_dir(__language__(30087), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=112',MODE_SHOW_RECO_T_G, i.cache.get(type, 112)+ti, 10)
        self._add_dir(__language__(30088), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=64',MODE_SHOW_RECO_T_G, i.cache.get(type, 64)+ti, 10)
        self._add_dir(__language__(30089), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=80',MODE_SHOW_RECO_T_G, i.cache.get(type, 80)+ti, 10)
        self._add_dir(__language__(30090), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=6',MODE_SHOW_RECO_T_G, i.cache.get(type, 6)+ti, 10)
        self._add_dir(__language__(30091), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=127',MODE_SHOW_RECO_T_G, i.cache.get(type, 127)+ti, 10)
        self._add_dir(__language__(30092), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=94',MODE_SHOW_RECO_T_G, i.cache.get(type, 94)+ti, 10)
        self._add_dir(__language__(30093), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=2',MODE_SHOW_RECO_T_G, i.cache.get(type, 2)+ti, 10)
        self._add_dir(__language__(30094), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=91',MODE_SHOW_RECO_T_G, i.cache.get(type, 91)+ti, 10)
        self._add_dir(__language__(30095), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=10',MODE_SHOW_RECO_T_G, i.cache.get(type, 10)+ti, 10)
        self._add_dir(__language__(30097), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=123',MODE_SHOW_RECO_T_G, i.cache.get(type, 123)+ti, 10)
        self._add_dir(__language__(30096), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=null',MODE_SHOW_RECO_T_G, i.access.get('default')+ti, 10)
        self.setContent('songs')

    '''
        Add to directory
    '''
    def add_to_directory(self, list, context = 'playlist'):
        n = len(list)
        if n < 1:
            self.showNotificationH("Qobuz", "Empty directory")
            return
        h = int(sys.argv[1])
        content_type = 'songs'
        if context == 'playlist':
            content_type = 'albums'
        if context == 'artists':
            content_type = 'artists'
        xbmcplugin.setContent(int(sys.argv[1]), content_type)
        xbmcplugin.addDirectoryItems(handle=h, items=list, totalItems=n)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_ALBUM)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_ALBUM_IGNORE_THE)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TRACKNUM)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_ARTIST)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_FILE)
        xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
        
    
    '''
        SHOW User Playlists
    '''
    def showUserPlaylists(self):
        user_playlists = qobuz.core.getUserPlaylists()
        list = user_playlists.get_items()
        self.add_to_directory(list)
        
    '''
        SHOW Playlist
    '''
    def showPlaylist(self, id):
        userid = qobuz.api.userid
        if (userid != 0):
            myplaylist = qobuz.core.getPlaylist(id)
            list = myplaylist.get_items()
            self.add_to_directory(list)
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok(__language__(30008), __language__(30034), __language__(30040))

    '''
        SHOW Product
    '''
    def showProduct (self, id, context_type = "playlist"):
        info(self, "showProduct(" + str(id) + ")")
        album = qobuz.core.getProduct(id,context_type)
        list = album.get_items()
        self.add_to_directory(list)

    '''
        SHOW Artsit
    '''
    def showArtist (self, id):
        album = qobuz.core.getProductsFromArtist()
        album.search_by_artist(id)
        if album.length() < 1:
            self.showNotification(30008, 30033)
            self.showCategories() 
            return
        list = album.get_items_by_artist()
        self.add_to_directory(list)

    # Get keyboard input
    def _get_keyboard(self, default="", heading="", hidden=False):
        kb = xbmc.Keyboard(default, heading, hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return unicode(kb.getText(), "utf-8")
        return ''

    # Add whatever directory
    def _add_dir(self, name, url, mode, iconimage, id, items=0):
        __language__= qobuz.lang
        if url == '':
            u=qobuz.boot.build_url(mode, id)
        else:
            u = url
        dir=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        dir.setInfo( type="Music", infoLabels={ "title": name.encode('utf8', 'ignore') } )
        dir.setProperty('fanart_image', os.path.join(qobuz.path.base, 'fanart.jpg'))
#        dir.setThumbnailImage(iconimage)
#        dir.setIconImage(iconimage)
        # Custom menu items
        menuItems = []
#        if mode == MODE_ALBUM:
#            mkplaylst=sys.argv[0]+"?mode="+str(MODE_MAKE_PLAYLIST)+"&name="+name+"&id="+str(id)
#            menuItems.append((__language__(30076), "XBMC.RunPlugin("+mkplaylst+")"))
#        if mode == MODE_PLAYLIST:
#            rmplaylst=sys.argv[0]+"?mode="+str(MODE_REMOVE_PLAYLIST)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
#            menuItems.append((__language__(30077), "XBMC.RunPlugin("+rmplaylst+")"))
#            mvplaylst=sys.argv[0]+"?mode="+str(MODE_RENAME_PLAYLIST)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
#            menuItems.append((__language__(30078), "XBMC.RunPlugin("+mvplaylst+")"))
        
        ''' MANAGE PLAYLIST '''
        manageplaylist=sys.argv[0]+"?mode="+str(MODE_MANAGE_PLAYLIST)
        menuItems.append((__language__(31010), "XBMC.RunPlugin("+manageplaylist+")"))
        ''' ERASE CACHE '''
        erasecache=sys.argv[0]+"?mode="+str(MODE_ERASE_CACHE)
        menuItems.append((__language__(31009), "XBMC.RunPlugin("+erasecache+")"))
        dir.setPath(u)
        dir.setProperty('path', u)
        dir.addContextMenuItems(menuItems, replaceItems=True)
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=dir,isFolder=True, totalItems=items)
