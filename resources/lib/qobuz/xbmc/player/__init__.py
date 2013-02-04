'''
    qobuz.xbmc.player
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
__all__ = ['Player']

from xbmcpy.mock.xbmc import xbmc
from xbmcpy.mock.xbmcgui import xbmcgui
from qobuz.debug import warn
from xbmcpy.util import notifyH, isFreeAccount, lang, setResolvedUrl, \
    getSetting
from qobuz.node import Flag, getNode

"""
    @class: QobuzPlayer
"""
keyTrackId = 'QobuzPlayerTrackId'

class Player(xbmc.Player):

    def __init__(self, **ka):
        super(Player, self).__init__()
        self.plugin = ka['plugin'] if 'plugin' in ka else None
        self.track_id = None
        self.total = None
        self.elapsed = None

    """
        Playing track given a track id
    """
    def play(self, renderer, node):
        track = node#getNode(Flag.TRACK, {'nid': track_id})
        
        if not track.fetch():
            warn(self, "Cannot get track data")
#            label = "Maybe an invalid track id"
#            item = xbmcgui.ListItem("No track information", label, '', 
#                                    getImage('icon-error-256'), '')
            return False
        if not track.is_playable:
            warn(self, "Cannot get streaming URL")
            return False
        item = renderer.itemFactory.make_item(node)
        track.item_add_playing_property(item)
        '''Some tracks are not authorized for stream and a 60s sample is
        returned, in that case we overwrite the song duration
        '''
        if track.is_sample():
            item.setInfo(
                'music', infoLabels={
                'duration': 60,
            })
            '''Don't warn for free account (all songs except purchases are 60s
            limited)
            '''
            if not isFreeAccount():
                notifyH("Qobuz", "Sample returned")
#        xbmcgui.Window(10000).setProperty(keyTrackId, str(node.nid)) 
        """
            Notify
        """
        if getSetting('notification_playingsong', isBool=True):
            notifyH(lang(34000), track.get_label(), track.get_image())
        """
            We are called from playlist...
        """
        if self.plugin.handle() == -1:
            super(Player, self).play(track.get_streaming_url(), 
                                          item, False)
        else:
            setResolvedUrl(handle=self.plugin.handle(),
                succeeded=True,
                listitem=item)
        return True
