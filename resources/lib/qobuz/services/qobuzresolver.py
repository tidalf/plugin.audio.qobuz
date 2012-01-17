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
import time
import re
import atexit
import xbmcaddon
import xbmc
import signal

__addon_name__   = 'plugin.audio.qobuz'
__addon_url__    = 'plugin://' + __addon_name__ + '/'
__addon__        = xbmcaddon.Addon(id=__addon_name__)
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__cwd__          = __addon__.getAddonInfo('path')

addonDir  = __addon__.getAddonInfo('path')
libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
qobuzDir = xbmc.translatePath(os.path.join(libDir, 'qobuz'))
sys.path.append(libDir)
sys.path.append(qobuzDir)
import qobuz
from bootstrap import QobuzBootstrap
boot = QobuzBootstrap(__addon__, 0)
boot.bootstrap_api()
boot.bootstrap_core()

__pid_file__ = 'qobuzresolver.pid'
__sleep__ = 5

from utils.tag import QobuzTagTrack
from data.track import QobuzTrack
from utils.pid import Pid


class QobuzResolver():
    
    def __init__(self):
        pass

        
service_name = 'Qobuz URL Resolver'

def log(msg, lvl = xbmc.LOGNOTICE):
    msg = service_name + ': ' + str(msg)
    try:
        xbmc.log(msg, lvl)
    except:
        print msg + "\n"
        
def login():
    user =  qobuz.addon.getSetting('username')
    password = qobuz.addon.getSetting('password')
    if not user or not password:
        log("You need to enter login/password in Qobuz Addon Settings")
        return False
    log("Login as user: " + str(user))
    return qobuz.api.login( user, password)

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
    if not cpath.startswith(__addon_url__): 
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
    track = qobuz.api.get_track(id)
    if not track:
        log("Cannot get QobuzTrack with id: " + str(id))
        return None
    tag = QobuzTagTrack(track)
    item = tag.getXbmcItem('player')
    item.setProperty('url', filename)
    item.setProperty('streaming_url', stream_url['streaming_url'])
    format_id = int(stream_url['format_id'])
    if format_id == 6:
        log("Setting mime type to audio/flac")
        item.setProperty('mimetype', 'audio/flac')
    elif format_id == 5:
        log("Setting mime type to audio/mpeg")
        item.setProperty('mimetype', 'audio/mpeg')
    else:
        log("Unknown format type: " + str(format_id))
        log("Setting mime type to audio/flac")
        item.setProperty('mimetype', 'audio/flac')
    item.setProperty('IsPlayable', 'true')
    item.setProperty('Music', 'true')
    return item

'''
'''
def parse_filename_for_id(filename):
    match = re.search('^'+__addon_url__+'?.*id=(\d+).*$', filename)
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
    stream_url = qobuz.api.get_track_url(id, 'playlist', 0, 6)
    if not stream_url:
        log("Cannot retrieve streaming url!")
        return None
    log(" - streaming_url: " + stream_url['streaming_url'])
    log(" - stream_type  : " + stream_url['streaming_type'])
    xitem = get_xbmc_item(item, pos, id, stream_url, filename)
    return replace_playlist_path(playlist, pos, xitem)

'''
    Do we have something to resolve
    Return: None if ok
            positon on error
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
    if not item.getfilename().startswith(__addon_url__):
        #print "We don't need to resolve this url"
        return False
    return resolve_position(player, playlist, item, position)

def gui_setting_enabled(pid):
    e = None
    try:
        e = qobuz.addon.getSetting('resolver_enabled')
    except:
        print "Cannot get addon setting..."
    if not e:
        log("We are not logged... Exiting!")
        return False
    elif e != 'true':
        log("Disabled from GUI settings... Exiting!")
        return False
    return True

'''
    Our watcher infinite loop
    We are put all our work in a try/catch block so our have
    lesser chance to die. Pid file is not unlinked on crash ...
    TODO: If plugin has never been launched cache path doesn't exist,
    our pid file can't be created, our service die ...
'''
'''
    MAIN
'''
pid_path = os.path.join(qobuz.path.cache, __pid_file__)
pid_id =  os.getpid()
pid = Pid(pid_path, pid_id)
pid.set_old_pid_age(__sleep__ * 5)
playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
current_pos = None
previous_pos = None
    
def watcher():
    watch_retry = 3
    if not pid.can_i_run():
        log("PID exists... exiting!")
        exit(0)
    if not pid.create():
        log("Cannot create PID")
        exit(0)
    log("Starting")
    __timetowork__ = __sleep__
    run = True
    while (run):
        run = False
        try:
            run = not xbmc.abortRequested
        except:
            run = False
            log("Cannot get xbmc.abortRequested value... exiting!")
            pid.remove()
            exit(0)
        if not run:
            print "Not running removing pid"
            pid.remove()
            exit(0)
        if not gui_setting_enabled(pid):
            log("Disabled from GUI... exiting!")
            pid.remove()
            exit(0)
        if __timetowork__ > 0:
            __timetowork__-=1
            time.sleep(1)
            continue
        else:
            __timetowork__ = __sleep__
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
        if not pid.touch():
            log('Cannot touch pid file: ' + pid.file)
        else:
            log('Touching pid file: ' + pid.file)
    if not pid.remove():
        log("Cannot remove pid file: " + pid.file)
    log("Exiting...")



atexit.register(pid.remove)

if __name__ == "__main__":
    if not gui_setting_enabled(pid):
        exit(0)
    watcher()
        
    
