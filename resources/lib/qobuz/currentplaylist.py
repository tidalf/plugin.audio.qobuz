import sys
import xbmc
import xbmcgui
import xbmcplugin 

class XbmcCurrentPlaylist():
    
    def __init__(self):
        xbmc.log("Init")
    
    def add_to_directory(self):
        xp = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        print "Playlist size: " + str(xp.size())
        for x in range(0, xp.size()):
            print "Filename: " + xp[x].getdescription()
            item = xbmcgui.ListItem(xp[x].getdescription())
            item.setInfo(type="Music", infoLabels={
                                                   "title":  xp[x].getdescription(),
                                                   "duration": xp[x].getduration(),
                                                   })
            item.setPath(xp[x].getdescription())
            item.setProperty('Music','true')
            item.setProperty('IsPlayable','true');
            item.setProperty('mimetype','audio/flac')
            #item.setThumbnailImage(t['album']['image']['large'])
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]) ,url=xp[x].getfilename() ,listitem=item,isFolder=False,totalItems=xp.size())
