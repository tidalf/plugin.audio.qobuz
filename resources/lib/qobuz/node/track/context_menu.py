from qobuz.constants import Mode
from qobuz.gui.util import lang, runPlugin, containerUpdate
from qobuz.node import Flag
from qobuz.theme import theme

def attach_context_menu(node, item, menu):
    if node.parent and (node.parent.nt & Flag.PLAYLIST == Flag.PLAYLIST):
        url = node.parent.make_url(
            nt=Flag.PLAYLIST,
            nid=node.parent.nid,
            qid=node.get_playlist_track_id(),
            nm='gui_remove_track',
            mode=Mode.VIEW)
        menu.add(path='playlist/remove',
                label=lang(30075),
                cmd=runPlugin(url),
                color=theme.get('item/caution/color'))
    label = node.get_album_label(default=None)
    if label is not None:
        label_id = node.get_album_label_id()
        url = node.make_url(nt=Flag.LABEL, nid=label_id, mode=Mode.VIEW)
        menu.add(path='label/view',
                label='View label (i8n): %s' % label,
                cmd=containerUpdate(url))
    return menu