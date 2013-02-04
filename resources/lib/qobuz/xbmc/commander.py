from node.renderer.xbmc import Commander
from xbmcpy.util import notifyH, lang
from xbmcpy.mock.xbmcgui import xbmcgui
from qobuz.node import getNode, Flag

class QobuzXbmcCommander(Commander):

    def action_favorites_add_tracks(self, plugin, node):
        print "Adding tracks to favorite"
        dialogHeading = lang(32001)
        parameters = node.parameters.copy()
        qnid = node.get_parameter('qnid')
        if qnid:
            parameters['nid'] = qnid
        else:
            if 'nid' in parameters:
                del parameters['nid']
        target = getNode(node.get_parameter('qkind'), parameters)
        nodes = node.list_tracks(plugin, target)
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