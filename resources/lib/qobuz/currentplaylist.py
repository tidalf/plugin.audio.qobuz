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
import xbmc
import xbmcgui
import xbmcplugin 

class XbmcCurrentPlaylist():
    
    def __init__(self, Core):
        self.Core = Core
        
    def add_to_directory(self):
        xp = self.Core.Bootstrap.Player.PlayList(xbmc.PLAYLIST_MUSIC)
        n = xp.size()
        for x in range(0, xp.size()):
            print "Filename: " + xp[x].getdescription()
            item = xbmcgui.ListItem(xp[x].getdescription())
            item.setInfo(type="Music", infoLabels={
                                                   "title":  xp[x].getdescription(),
                                                   "duration": xp[x].getduration(),
                                                   })
            item.setPath(xp[x].filename())
            #item.setProperty('Music','true')
            #item.setProperty('IsPlayable','true');
            #item.setProperty('mimetype','audio/flac')
            #item.setThumbnailImage(t['album']['image']['large'])
            self.Core.GUI.addDirectoryItem(self.Core.Bootstrap.__handle__, xp[x].getfilename(), item, False, xp.size())
            #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]) ,url=xp[x].getfilename(),item,False,n)
