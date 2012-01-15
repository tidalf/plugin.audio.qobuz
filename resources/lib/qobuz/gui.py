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
import urllib

import xbmcplugin
import xbmcgui
import xbmc

from constants import *
from debug import info, warn, log

'''
    CLASS QobuzGUI
'''
class QobuzGUI:

    def __init__( self, bootstrap):
        self.Bootstrap = bootstrap
        xbmcplugin.setProperty(int(sys.argv[1]), 'Music', 'Qobuz')
        

    '''
    Must be called at the end for folder to be displayed
    '''
    def endOfDirectory(self):
#        self.setFanArt()
#        xbmcplugin.setContent(int(sys.argv[1]), 'songs')
#        xbmcplugin.setPluginFanart(int(sys.argv[1]), 'special://home/addons/plugin.audio.qobuz/fanart.jpg', color2='0xFFFF3300')
#        xbmc.executebuiltin('SetProperty(View,Thumbnails)')
        ''' SEARCH '''
        if self.Bootstrap.MODE and self.Bootstrap.MODE <= 5: 
            return xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=False, cacheToDisc=True)
        elif self.Bootstrap.MODE == MODE_SHOW_RECO_T_G:
             return xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=False, cacheToDisc=False)
        else:
            return xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=False, cacheToDisc=True)
    
    '''
        SHOW Notification (HUMAN ONE / NO i8n)
    '''
    def showNotificationH(self, title, text):
        title = unicode(title, "utf-8", errors="replace")
        text = unicode(text, "utf-8", errors="replace")
        s = 'XBMC.Notification(' + title + ',' + text + ', 2000, ' + self.Bootstrap.Images.get('default') + ')'
        try:
            xbmc.executebuiltin(s)
        except:
            warn(self, "Notification failure")
            
    '''
        SHOW Notification
    '''
    def showNotification(self, title, text):
        self.setFanArt()   
        __language__ = self.Bootstrap.__language__
        xbmc.executebuiltin('XBMC.Notification(' + __language__(title) + ',' + __language__(text)+ ', 2000, ' + self.Bootstrap.Images.get('default') + ')')

    '''
        SET FanArt
    '''
    def setFanArt(self, fanart = 'fanart'):
        xbmcplugin.setPluginFanart(self.Bootstrap.__handle__,  self.Bootstrap.Images.get('default'))
      
    '''
        SET Content
    '''
    def setContent(self, content):
        '''
        *Note, You can use the above as keywords for arguments.
        content: files, songs, artists, albums, movies, tvshows, episodes, musicvideos
        http://xbmc.sourceforge.net/python-docs/xbmcplugin.html
        '''
        xbmcplugin.setContent(self.Bootstrap.__handle__, content)

    '''
        MUST BE REMOVED ?
    '''  
    def addDirectoryItem(self, u, item, bFolder, len):
        xbmcplugin.addDirectoryItem(handle=self.Bootstrap.__handle__, 
                                    url=u, listitem=item, isFolder=bFolder, 
                                    totalItems=len)

    def showLoginFailure(self):
        __language__ = self.Bootstrap.__language__
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30008), __language__(30034), __language__(30040))
        
    '''
        Top-level menu
    '''
    def showCategories(self):
        i = self.Bootstrap.Images
        __language__ = self.Bootstrap.__language__
        if not self.Bootstrap.META:
            self._add_dir(__language__(30013), '', MODE_SEARCH_SONGS, i.get('song'), 0)
            self._add_dir(__language__(30014), '', MODE_SEARCH_ALBUMS, i.get('album'), 0)
            self._add_dir(__language__(30015), '', MODE_SEARCH_ARTISTS, i.get('album'), 0)
        self._add_dir(__language__(30082), '', MODE_SHOW_RECOS, i.get('song'), 0)
        self._add_dir(__language__(30101), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=new-releases', MODE_SHOW_RECO_T, i.get('song'), 0)
        self._add_dir(__language__(30100), '', MODE_SHOW_PURCHASES, i.get('song'), 0)
        if (self.Bootstrap.Core.Api.userid != 0):
            self._add_dir(__language__(30019), '', MODE_USERPLAYLISTS, i.get('playlist'), 0)
        self.setContent('albums')
        

    """
        SEARCH for songs
    """
    def searchSongs(self):
        __language__ = self.Bootstrap.__language__
        query = self._get_keyboard(default="",heading=__language__(30020))
        query = query.strip()
        if (query != ''):
            s = self.Bootstrap.Core.getQobuzSearchTracks()
            s.search(query, self.Bootstrap.__addon__.getSetting('songsearchlimit'))
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
        __language__ = self.Bootstrap.__language__
        query = self._get_keyboard(default="",heading=__language__(30022))
        query = query.strip()
        if (query != ''):
            s = self.Bootstrap.Core.getQobuzSearchAlbums()
            s.search(query, self.Bootstrap.__addon__.getSetting('albumsearchlimit'))
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
        __language__ = self.Bootstrap.__language__
        query = self._get_keyboard(default="",heading=__language__(30024))
        query = query.strip()
        if (query != ''):
            s = self.Bootstrap.Core.getQobuzSearchArtists()
            s.search(query, self.Bootstrap.__addon__.getSetting('artistsearchlimit'))
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
            r = self.Bootstrap.Core.getRecommandation(genre_id, type)
            list = r.get_items()
            self.add_to_directory(list)
        else:
            self.showNotificationH('Qobuz', 'No genre_id for recommandation')
            self.showCategories()

    '''
        SHOW Purchases
    '''
    def showPurchases(self):
        r = self.Bootstrap.Core.getPurchases()
        list = r.get_items()
        self.add_to_directory(list)

    '''
        SHOW Recommandations Types
    '''
    def showRecommendationsTypes(self):
        __language__ = self.Bootstrap.__language__
        i = self.Bootstrap.Images
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
        from data.genre_image import QobuzGenreImage
        import time
        import math
        ti = '?t='+str(int(time.time()))
        genre = QobuzGenreImage(self.Bootstrap.Core)
        __language__ = self.Bootstrap.__language__
        i = self.Bootstrap.Images
        self._add_dir(__language__(30087), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=112',MODE_SHOW_RECO_T_G, genre.get(type, 112)+ti, 10)
        self._add_dir(__language__(30088), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=64',MODE_SHOW_RECO_T_G, genre.get(type, 64)+ti, 10)
        self._add_dir(__language__(30089), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=80',MODE_SHOW_RECO_T_G, genre.get(type, 80)+ti, 10)
        self._add_dir(__language__(30090), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=6',MODE_SHOW_RECO_T_G, genre.get(type, 6)+ti, 10)
        self._add_dir(__language__(30091), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=2',MODE_SHOW_RECO_T_G, genre.get(type, 64)+ti, 10)
        self._add_dir(__language__(30092), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=94',MODE_SHOW_RECO_T_G, genre.get(type, 94)+ti, 10)
        self._add_dir(__language__(30093), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=2',MODE_SHOW_RECO_T_G, genre.get(type, 2)+ti, 10)
        self._add_dir(__language__(30094), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=91',MODE_SHOW_RECO_T_G, genre.get(type, 91)+ti, 10)
        self._add_dir(__language__(30095), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=10',MODE_SHOW_RECO_T_G, genre.get(type, 10)+ti, 10)
        self._add_dir(__language__(30097), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=123',MODE_SHOW_RECO_T_G, genre.get(type, 123)+ti, 10)
        self._add_dir(__language__(30096), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=null',MODE_SHOW_RECO_T_G, i.genre(0)+ti, 10)
        self.setContent('songs')

    '''
        Add to directory
    '''
    def add_to_directory(self, list):
        n = len(list)
        if n < 1:
            self.showNotificationH("Qobuz", "Empty directory")
            return
        h = int(sys.argv[1])
        xbmcplugin.addDirectoryItems(handle=h, items=list, totalItems=n)
    
    '''
        SHOW User Playlists
    '''
    def showUserPlaylists(self):
        user_playlists = self.Bootstrap.Core.getUserPlaylists()
        list = user_playlists.get_items()
        self.add_to_directory(list)
        
    '''
        SHOW Playlist
    '''
    def showPlaylist(self, id):
        userid = self.Bootstrap.Core.Api.userid
        if (userid != 0):
            myplaylist = self.Bootstrap.Core.getPlaylist(id)
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
        album = self.Bootstrap.Core.getProduct(id,context_type)
        list = album.get_items()
        self.add_to_directory(list)

    '''
        SHOW Artsit
    '''
    def showArtist (self, id):
        album = self.Bootstrap.Core.getProductsFromArtist()
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
        __language__= self.Bootstrap.__language__
        if url == '':
            u=self.Bootstrap.build_url(mode, id)
        else:
            u = url
        dir=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        dir.setInfo( type="Music", infoLabels={ "title": name } )
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
        #dir.setProperty('IsFolder', 'true')
        #exit(0)
        #self.Bootstrap.WIN.getControl(50).addItem(dir)
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=dir,isFolder=True, totalItems=items)
