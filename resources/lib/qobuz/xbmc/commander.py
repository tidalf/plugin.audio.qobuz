'''
    qobuz.xbmc.commander
    ~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from node.renderer.xbmc import Commander
from xbmcpy.util import notifyH, lang, executeBuiltin, containerUpdate
from xbmcpy.mock.xbmcgui import xbmcgui
from qobuz.node import getNode, Flag
from xbmcpy.mock import xbmcaddon

base_url = 'plugin://%s/' % (xbmcaddon.Addon().getAddonInfo('id'))

class QobuzXbmcCommander(Commander):

    def action_favorite_add_tracks(self, plugin, node, tnode):
        target = node
        if tnode:
            target = tnode
        nodes = target.list_tracks(plugin, node)
        if len(nodes) == 0:
            return False
        ret = xbmcgui.Dialog().select(lang(32001), [
           node.get_label() for node in nodes
        ])
        if ret == -1:
            return False
        track_ids = ','.join([str(node.nid) for node in nodes])
        if not self.add_tracks(track_ids):
            notifyH(dialogHeading, 'Cannot add track(s) to favorite')
            return False
        notifyH(dialogHeading, 'Track(s) added to favorite')
        return True

    def action_similar_artist_get(self, plugin, node, tnode):
        if not hasattr(node, 'get_artist_id'):
            return False
#        node.fetch(None)
        tnode.nid = node.get_artist_id()
        url = '%s%s' % (base_url, tnode.url())
        executeBuiltin(containerUpdate(url))
        return True
