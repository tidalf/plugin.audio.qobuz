from qobuz.api.user import current as user
from qobuz.constants import Mode
from qobuz.gui.util import containerUpdate
from qobuz.gui.util import lang, runPlugin
from qobuz.node import Flag
from qobuz.theme import theme, color as color_helper


# Color helper
def color(txt):
    return color_helper(theme.get('menu/playlist/color'), txt)


def attach_context_menu(node, item, menu):
    isOwner = True
    cmd = containerUpdate(
        node.make_url(
            nt=Flag.USERPLAYLISTS, id='', mode=Mode.VIEW))
    menu.add(path='playlist',
             pos=1,
             label='Playlist',
             cmd=cmd,
             mode=Mode.VIEW)
    if user.username != node.get_property('owner/name'):
        isOwner = False
    if isOwner:
        url = node.make_url(
            nt=Flag.PLAYLIST, mode=Mode.VIEW, nm='set_as_current')
        menu.add(path='playlist/set_as_current', label=color(lang(30163)),
                 cmd=containerUpdate(url))

        url = node.make_url(nt=Flag.PLAYLIST, nm='gui_rename')
        menu.add(path='playlist/rename', label=color(lang(30165)),
                 cmd=runPlugin(url))
        url = node.make_url(
            nt=Flag.PLAYLIST, mode=Mode.VIEW, nm='toggle_privacy')
        menu.add(path='playlist/toggle_privacy', post=2,
                 label=color('Toggle privacy'), cmd=containerUpdate(url))
    elif node.parent and node.parent.nt & (Flag.ALL ^ Flag.USERPLAYLISTS):
        url = node.make_url(nt=Flag.PLAYLIST, nm='subscribe')
        menu.add(path='playlist/subscribe', label=color(lang(30168)),
                 cmd=runPlugin(url))
    url = node.make_url(nt=Flag.PLAYLIST, nm='gui_remove')
    menu.add(path='playlist/remove', label=color(lang(30166)),
             cmd=runPlugin(url), color=theme.get('item/caution/color'))
