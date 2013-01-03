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
import xbmcplugin
import xbmcgui

import qobuz
from debug import warn
from gui.util import notifyH, isFreeAccount, lang, setResolvedUrl, getImage
from node.flag import NodeFlag as Flag
from node.track import Node_track
#from fakeipc import FakeIPC

"""
    @class: QobuzPlayer
"""
class QobuzPlayer(xbmc.Player):

    def __init__(self, **ka):
        ka['type'] = xbmc.PLAYER_CORE_AUTO
        super(QobuzPlayer, self).__init__()
        self.track_id = None
        self.total = None
        self.elapsed = None
        #self.IPC = FakeIPC('Qobuz.IPC.Player')

    """
        Playing track given a track id
    """
    def play(self, track_id):
        node = Node_track(None, {'nid': track_id})
        node.pre_build_down(None, 1, Flag.TRACK)
        xbmcgui.Window(10000).setProperty("NID", track_id) 
        #self.IPC.write({
        #            'nid': node.id,
        #            'nt': node.type,
        #            'streamingUrl': streaming_url,
        #})
        item = None
        if not node.data:
            warn(self, "Cannot get track data")
            label = "Maybe an invalid track id"
            item = xbmcgui.ListItem("No track information",
                                    label,
                                    '',
                                    getImage('icon-error-256'),
                                    '')
        else:
            item = node.makeListItem()
        if not node.get_mimetype():
            warn(self, "Cannot get streaming URL")
            return False
        # some tracks are not authorized for stream and a 60s sample is
        # returned, in that case we overwrite the song duration
        if node.is_sample():
            item.setInfo(
                'music', infoLabels={
                'duration': 60,
                })
            # don't warn for free account (all songs except purchases are 60s
            # limited)
            if not isFreeAccount():
                notifyH("Qobuz", "Sample returned")
        """
            Notify
        """
        if qobuz.addon.getSetting('notification_playingsong') == 'true':
            notifyH(lang(34000), node.get_label(), node.get_image())
        """
            We are called from playlist...
        """
        if qobuz.boot.handle == -1:
            super(QobuzPlayer, self).play(node.get_streaming_url(), 
                                          item, False)
        else:
            setResolvedUrl(handle=qobuz.boot.handle,
                succeeded=True,
                listitem=item)
        return True
