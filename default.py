#     Copyright 2011 Stephen Denham, Joachim Basmaison, Cyril Leclerc
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

'''
 Bootstrap
'''
import os
import sys
import xbmcaddon

__addon__ = xbmcaddon.Addon('plugin.audio.qobuz')
addonDir  = __addon__.getAddonInfo('path')
libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
sys.path.append(libDir)
#from qobuz.constants import *
from qobuz.bootstrap import *
Core = QobuzBootstrap(__addon__)
Core.parse_sys_args()
Core.mode_dispatch()
sys.exit(0)


#import urllib, sys, os, shutil, re, pickle, time, tempfile
#import xbmcaddon, xbmcplugin, xbmcgui, xbmc
#import pprint

#__addon__     = xbmcaddon.Addon('plugin.audio.qobuz')
#__addonname__ = __addon__.getAddonInfo('name')
#__cwd__       = __addon__.getAddonInfo('path')
#__author__    = __addon__.getAddonInfo('author')
#__version__   = __addon__.getAddonInfo('version')
#__language__  = __addon__.getLocalizedString
#__debugging__    = __addon__.getSetting('debug')
#
#MODE_SEARCH_SONGS = 1
#MODE_SEARCH_ALBUMS = 2
#MODE_SEARCH_ARTISTS = 3
#MODE_SEARCH_ARTISTS_ALBUMS = 4
#MODE_SEARCH_PLAYLISTS = 5
#MODE_ARTIST_POPULAR = 6
#MODE_POPULAR_SONGS = 7
#MODE_FAVORITES = 8
#MODE_PLAYLISTS = 9
#MODE_ALBUM = 10
#MODE_ARTIST = 11
#MODE_PLAYLIST = 12
#MODE_SONG_PAGE = 13
#MODE_SIMILAR_ARTISTS = 14
#MODE_SHOW_RECOS = 15
#MODE_SHOW_RECO_T = 16
#MODE_SHOW_RECO_T_G = 17
#MODE_SONG = 30
#MODE_FAVORITE = 31
#MODE_UNFAVORITE = 32
#MODE_MAKE_PLAYLIST = 33
#MODE_REMOVE_PLAYLIST = 34
#MODE_RENAME_PLAYLIST = 35
#MODE_REMOVE_PLAYLIST_SONG = 36
#MODE_ADD_PLAYLIST_SONG = 37


#ACTION_MOVE_LEFT = 1
#ACTION_MOVE_UP = 3
#ACTION_MOVE_DOWN = 4
#ACTION_PAGE_UP = 5
#ACTION_PAGE_DOWN = 6
#ACTION_SELECT_ITEM = 7
#ACTION_PREVIOUS_MENU = 10
#
## Formats for track labels
#ARTIST_ALBUM_NAME_LABEL = 0
#NAME_ALBUM_ARTIST_LABEL = 1
#
## Stream marking time (seconds)
#STREAM_MARKING_TIME = 30
#
## Timeout
#STREAM_TIMEOUT = 30
#
#songMarkTime = 0
## player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
#playTimer = None
##playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
#
##baseDir = __cwd__
#resDir = xbmc.translatePath(os.path.join(baseDir, 'resources'))
#libDir = xbmc.translatePath(os.path.join(resDir,  'lib'))
#imgDir = xbmc.translatePath(os.path.join(resDir,  'img'))
#cacheDir = os.path.join(xbmc.translatePath('special://masterprofile/addon_data/'), os.path.basename(baseDir))
#thumbDirName = 'thumb'
#thumbDir = os.path.join(xbmc.translatePath('special://masterprofile/addon_data/'), os.path.basename(baseDir), thumbDirName)
#
#baseModeUrl = 'plugin://plugin.audio.qobuz/'
#playlistUrl = baseModeUrl + '?mode=' + str(MODE_PLAYLIST)
#playlistsUrl = baseModeUrl + '?mode=' + str(MODE_PLAYLISTS)
#favoritesUrl = baseModeUrl + '?mode=' + str(MODE_FAVORITES)
#
#searchArtistsAlbumsName = __language__(30006)
#
#thumbDef = os.path.join(imgDir, 'default.tbn')
#listBackground = os.path.join(imgDir, 'listbackground.png')
#

#__addon__     = xbmcaddon.Addon('plugin.audio.qobuz')
#__addonname__ = __addon__.getAddonInfo('name')
#__cwd__       = __addon__.getAddonInfo('path')
#
#baseDir = __cwd__
#resDir = xbmc.translatePath(os.path.join(baseDir, 'resources'))
#libDir = xbmc.translatePath(os.path.join(resDir,  'lib'))
#sys.path.append (libDir)
#qobuzDir = xbmc.translatePath(os.path.join(libDir,  'qobuz'))
#sys.path.append (qobuzDir)

#from GroovesharkAPI import GrooveAPI




































#exit
#from qobuz.qobuz import QobuzXbmc
#from qobuz.api import QobuzApi
#from qobuz.constants import *
# Parse URL parameters

#def get_params():
#  param=[]
#  paramstring=sys.argv[2]
#  if __debugging__ :
#     xbmc.log(paramstring)
#  if len(paramstring)>=2:
#     params=sys.argv[2]
#     cleanedparams=params.replace('?','')
#     if (params[len(params)-1]=='/'):
#        params=params[0:len(params)-2]
#     pairsofparams=cleanedparams.split('&')
#     param={}
#     for i in range(len(pairsofparams)):
#        splitparams={}
#        splitparams=pairsofparams[i].split('=')
#        if (len(splitparams))==2:
#          param[splitparams[0]]=splitparams[1]
#  return param
#
#params=get_params()
#mode=None
#try: mode=int(params["mode"])
#except: pass
#
#qob = None
##try:
#qob = QobuzXbmc(baseDir)
#settings = xbmcaddon.Addon(id='plugin.audio.qobuz')
#if not qob.login(settings.getSetting('username'), settings.getSetting('password')):
#  print "Cannot login, abort...\n"
#  exit(0)
#try: pass
#except:
#  dialog = xbmcgui.Dialog(__language__(30008),__language__(30009),__language__(30010))
#  dialog.ok(__language__(30008),__language__(30009))
#  sys.exit(-1)
#
#
## Window dialog to select a grooveshark playlist
#class QobuzPlaylistSelect(xbmcgui.WindowDialog):
#
#  def __init__(self, items=[]):
#     gap = int(self.getHeight()/100)
#     w = int(self.getWidth()*0.5)
#     h = self.getHeight()-30*gap
#     rw = self.getWidth()
#     rh = self.getHeight()
#     x = rw/2 - w/2
#     y = rh/2 -h/2
#
#     self.imgBg = xbmcgui.ControlImage(x+gap, 5*gap+y, w-2*gap, h-5*gap, listBackground)
#     self.addControl(self.imgBg)
#
#     self.playlistControl = xbmcgui.ControlList(2*gap+x, y+3*gap+30, w-4*gap, h-10*gap, textColor='0xFFFFFFFF', selectedColor='0xFFFF4242', itemTextYOffset=0, itemHeight=50, alignmentY = 0)
#     self.addControl(self.playlistControl)
#
#     self.lastPos = 0
#     self.isSelecting = False
#     self.selected = -1
#     listitems = []
#     for playlist in items:
#        listitems.append(xbmcgui.ListItem(playlist[0]))
#     listitems.append(xbmcgui.ListItem(__language__(30011)))
#     self.playlistControl.addItems(listitems)
#     self.setFocus(self.playlistControl)
#     self.playlistControl.selectItem(0)
#     item = self.playlistControl.getListItem(self.lastPos)
#     item.select(True)
#
#  # Highlight selected item
#  def setHighlight(self):
#     if self.isSelecting:
#        return
#     else:
#        self.isSelecting = True
#
#     pos = self.playlistControl.getSelectedPosition()
#     if pos >= 0:
#        item = self.playlistControl.getListItem(self.lastPos)
#        item.select(False)
#        item = self.playlistControl.getListItem(pos)
#        item.select(True)
#        self.lastPos = pos
#     self.isSelecting = False
#
#  # Control - select
#  def onControl(self, control):
#     if control == self.playlistControl:
#        self.selected = self.playlistControl.getSelectedPosition()
#        self.close()
#
#  # Action - close or up/down
#  def onAction(self, action):
#     if action == ACTION_PREVIOUS_MENU:
#        self.selected = -1
#        self.close()
#     elif action == ACTION_MOVE_UP or action == ACTION_MOVE_DOWN or action == ACTION_PAGE_UP or action == ACTION_PAGE_DOWN == 6:
#        self.setFocus(self.playlistControl)
#        self.setHighlight()





## Mark song as playing or played
#def markSong(songid, duration, streamKey, streamServerID):
#     global songMarkTime
#     global playTimer
#     global player
#     if player.isPlayingAudio():
#          tNow = player.getTime()
#          if tNow >= STREAM_MARKING_TIME and songMarkTime == 0:
#                # SHO #
#                #groovesharkApi.markStreamKeyOver30Secs(streamKey, streamServerID)
#                # SHO #
#                songMarkTime = tNow
#          elif duration > tNow and duration - tNow < 2 and songMarkTime >= STREAM_MARKING_TIME:
#                playTimer.cancel()
#                songMarkTime = 0
#                # SHO #
#                #groovesharkApi.markSongComplete(songid, streamKey, streamServerID)
#                # SHO #
#     else:
#          playTimer.cancel()
#          songMarkTime = 0
#
#class _Info:
#     def __init__( self, *args, **kwargs ):
#          self.__dict__.update( kwargs )
#class PlayTimer(Thread):
#     # interval -- floating point number specifying the number of seconds to wait before executing function
#     # function -- the function (or callable object) to be executed
#
#     # iterations -- integer specifying the number of iterations to perform
#     # args -- list of positional arguments passed to function
#     # kwargs -- dictionary of keyword arguments passed to function
#
#     def __init__(self, interval, function, iterations=0, args=[], kwargs={}):
#          Thread.__init__(self)
#          self.interval = interval
#          self.function = function
#          self.iterations = iterations
#          self.args = args
#          self.kwargs = kwargs
#          self.finished = Event()
#
#     def run(self):
#          count = 0
#          while not self.finished.isSet() and (self.iterations <= 0 or count < self.iterations):
#                self.finished.wait(self.interval)
#                if not self.finished.isSet():
#                     self.function(*self.args, **self.kwargs)
#                     count += 1
#
#     def cancel(self):
#          self.finished.set()
#
#     def setIterations(self, iterations):
#          self.iterations = iterations
#
#
#     def getTime(self):
#          return self.iterations * self.interval



#
#'''
#Main
#'''
#qobuz = QobuzGUI();
#qob._handle = qobuz._handle
#id=''
#try: id = str(params["id"])
#except: pass
#name = None
#try: name=urllib.unquote_plus(params["name"])
#except: pass
## Call function for URL
#if mode==None:
#  qobuz.categories()
#
#elif mode==MODE_SEARCH_SONGS:
#  qobuz.searchSongs()
#
#elif mode == MODE_SHOW_RECOS:
#  qobuz.showRecommendationsTypes()
#
#elif mode == MODE_SHOW_RECO_T_G:
#    try:
#        type=urllib.unquote_plus(params["type"])
#        genre=urllib.unquote_plus(params["genre"])
#    except: pass
#    qobuz.showRecommendations(type,genre)
#
#elif mode == MODE_SHOW_RECO_T:
#    try:
#        type=urllib.unquote_plus(params["type"])
#    except: pass
#    qobuz.showRecommendationsGenres(type)
#
#elif mode==MODE_SEARCH_ALBUMS:
#    qobuz.searchAlbums()
#
#elif mode==MODE_SEARCH_ARTISTS:
#    qobuz.searchArtists()
#
#elif mode==MODE_FAVORITES:
#    qobuz.favorites()
#
#elif mode==MODE_PLAYLISTS:
#    qobuz.playlists()
#
#elif mode == MODE_SONG:
#    t = qob.getTrack(str(id))
#    t.play()
#
#elif mode==MODE_ARTIST:
#  qobuz.artist(str(id))
#
#elif mode==MODE_ALBUM:
#  qobuz.product(str(id))
#
#elif mode==MODE_PLAYLIST:
#  qobuz.playlist(str(id), name)
#
#if mode < MODE_SONG:
#  xbmcplugin.endOfDirectory(int(sys.argv[1]))
