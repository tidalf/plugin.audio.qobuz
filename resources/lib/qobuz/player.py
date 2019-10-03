'''
    qobuz.player
    ~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

import xbmc, xbmcgui  # pylint:disable=E0401

from qobuz import config
from qobuz.debug import getLogger
from qobuz.gui.util import notifyH, isFreeAccount, lang, setResolvedUrl, notify_warn
from qobuz.node import Flag, getNode, helper

logger = getLogger(__name__)
keyTrackId = 'QobuzPlayerTrackId'


def notify_restriction(track):
    restrictions = ''
    for restriction in track.get_restrictions():
        restrictions += '%s\n' % restriction
    if restrictions != '':
        notify_warn("Restriction", restrictions, mstime=5000)


class QobuzPlayer(xbmc.Player):
    """
        @class: QobuzPlayer
    """

    def __init__(self, **ka):
        """ Constructor"""
        ka['type'] = 0
        super(QobuzPlayer, self).__init__()
        self.track_id = None
        self.total = None
        self.elapsed = None

    def play(self, track_id, params=None):
        """ Playing track given a track id """
        params = {} if params is None else params
        track = getNode(Flag.TRACK, {'nid': track_id})
        data = track.fetch(helper.TreeTraverseOpts(
            lvl=1,
            whiteFlag=Flag.TRACK,
            blackFlag=Flag.NONE))
        if data is None:
            logger.warn('Cannot get track data')
            return False
        track.data = data
        if not track.is_playable():
            logger.warn('Cannot get streaming URL')
            return False
        if 'purchased' in params:
            track.parameters['purchased'] = True
        item = track.makeListItem()
        track.item_add_playing_property(item)
        # Some tracks are not authorized for stream and a 60s sample is
        # returned, in that case we overwrite the song duration
        if track.is_sample():
            item.setInfo('Music', infoLabels={'duration': 60, })
            # Don't warn for free account (all songs except purchases are 60s
            # limited)

            if not isFreeAccount():
                notify_warn("Qobuz / Free Account", "Sample returned")
            if track.is_uncredentialed():
                notify_warn("Qobuz / Uncredentialed", "Sample returned")
        xbmcgui.Window(10000).setProperty(keyTrackId, track_id)
        # Notify
        if config.app.registry.get('notification_playingsong', to='bool'):
            notify_restriction(track)
            notifyH(lang(30132), track.get_label(), image=track.get_image())
        # We are called from playlist...
        if config.app.handle == -1:
            super(QobuzPlayer, self).play(track.get_streaming_url(), item,
                                          False)
        else:
            setResolvedUrl(
                handle=config.app.handle, succeeded=True, listitem=item)
        return True
