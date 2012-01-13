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
import time 
import re

import xbmcaddon
import xbmc

__addon__ = xbmcaddon.Addon(id='plugin.audio.qobuz')
addonDir  = __addon__.getAddonInfo('path')
libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
qobuzDir = xbmc.translatePath(os.path.join(libDir, 'qobuz'))
sys.path.append(libDir)
sys.path.append(qobuzDir)


from api import QobuzApi
from utils.tag import QobuzTagTrack
from data.track import QobuzTrack

service_name = 'Qobuz URL Resolver'

API = QobuzApi()

def log(msg, lvl = xbmc.LOGDEBUG):
    xbmc.log(service_name + ': ' + str(msg), lvl)

def login():
        user =  __addon__.getSetting('username')
        password = __addon__.getSetting('password')
        if not user or not password:
            log("You need to enter login/password in Qobuz Addon Settings")
            return False
        log("Login as user: " + str(user))
        return API.login( user, password)

'''
'''
def replace_playlist_path(playlist, cpos, item):
        try:
            i = playlist[cpos]
        except:
            log("Invalid playlist position: " + str(i))
            return False
        cpath = ''
        try:
            cpath = playlist[cpos].getfilename()
        except:
            print "Cannot get playlist filename\n"
            return False
        
        if not cpath:
            print "Current path is empty, abort\n"
            return False
        if not cpath.startswith('plugin://'): 
            print "We already have correct url in playlist... abort"
            return True
        item.setPath(cpath)
        item.setPath(item.getProperty('streaming_url'))
        playlist.remove(cpath)
        playlist.add(url=item.getProperty('streaming_url'), listitem=item, index=cpos)
        return True

'''
'''
def get_xbmc_item(p_item, pos, id, stream_url, filename):
    Core = None
    track = API.get_track(id)
    if not track:
        log("Cannot get QobuzTrack with id: " + str(id))
        return None
    tag = QobuzTagTrack(Core, track)
    item = tag.getXbmcItem('player')
    item.setProperty('url', filename)
    item.setProperty('streaming_url', stream_url['streaming_url'])
    item.setProperty('mimetype', 'audio/flac')
    item.setProperty('IsPlayable', 'true')
    item.setProperty('Music', 'true')
    return item

'''
'''
def parse_filename_for_id(filename):
    match = re.search('^plugin://plugin.audio.qobuz/?.*id=(\d+).*$', filename)
    if not match:
        return None
    return match.group(1)

'''
'''
def resolve_position(player, playlist, item, pos):
    filename = item.getfilename()
    id = parse_filename_for_id(filename)
    if not id:
        print "Cannot parse id for this url: " + filename + "\n"
        return None
    
    log("Need to resolve position " + str(pos))
    log(" - url: " + filename)
    log(" - id: " + str(id))
    if not login():
        log("Login to Qobuz fail, abort...")
        return None
    stream_url = API.get_track_url(id, 'playlist', 0, 6)
    if not stream_url:
        log("Cannot retrieve streaming url!")
        return None
    log(" - streaming_url: " + stream_url['streaming_url'])
    log(" - stream_type  : " + stream_url['streaming_type'])
    xitem = get_xbmc_item(item, pos, id, stream_url, filename)
    return replace_playlist_path(playlist, pos, xitem)

'''
    Do we have something to resolve
'''
def watch_playlist(player, playlist):
    size = playlist.size()
    item = None
    position = None
    try:
        position = playlist.getposition() + 1
        if not position:
            log("Cannot get position\n")
            return 
        log("Next position: " + str(position))
        item = playlist[position]
    except:
        log("Playlist item not found... abort")
        return
    if not item:
        log("No url to resolve at position " + str(position))
        return 
    if not item.getfilename().startswith('plugin://'):
        #print "We don't need to resolve this url"
        return False
    return resolve_position(player, playlist, item, position)


'''
    Our watcher infinite loop
    We are put all our work in a try/catch block so our have
    lesser chance to die. Pid file is not unliked on crash ...
'''
def watcher():
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
    pid = str(os.getpid())
    pidFile = os.path.join(xbmc.translatePath('special://temp/'), 'qobuzresolver.pid')
    if os.path.isfile(pidFile):
        print "%s already exists, exiting" % pidFile
        sys.exit(1)
    else:
        file(pidFile, 'w').write(pid)
    log("Starting")
    while (not xbmc.abortRequested):
        try:
            pl_size = playlist.size()
            if pl_size > 0 and player.isPlayingAudio():
                try:
                    log("Watching playlist (" + str(playlist.size()) + ")")
                    watch_playlist(player, playlist)
                except:
                    log('Something goes wrong with our resolver!')
        except:
            log('We are not playing audio!')
        time.sleep(5)
    log("Removing pid: " + pidFile)
    os.unlink(pidFile)
    log("Exiting...")
    sys.exit(0)


if __name__ == "__main__":
    watcher()
        
    