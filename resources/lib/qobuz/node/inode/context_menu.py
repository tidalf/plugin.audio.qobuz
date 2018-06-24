import urllib

from qobuz import config
from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.gui.util import lang, runPlugin, containerUpdate
from qobuz.node import Flag
from qobuz.theme import theme, color

logger = getLogger(__name__)


def attach_context_menu(node, item, menu):
    '''Note: Url made with make_url must set mode (like mode=Mode.VIEW)
        else we are copying current mode (for track it's Mode.PLAY ...)
    '''
    # HOME
    colorCaution = theme.get('item/caution/color')

    def c_pl(txt):
        return color(theme.get('menu/playlist/color'), txt)

    def c_fav(txt):
        return color(theme.get('menu/favorite/color'), txt)

    url = node.make_url(nt=Flag.ROOT, mode=Mode.VIEW, nm='')
    menu.add(path='qobuz',
             label="Qobuz",
             cmd=containerUpdate(url, False),
             id='',
             pos=-5)
    # ARTIST
    if node.nt & (Flag.ALBUM | Flag.TRACK | Flag.ARTIST):
        artist_id = node.get_artist_id()
        # Similar artist
        url = node.make_url(
            nt=Flag.SIMILAR_ARTIST, nid=artist_id, mode=Mode.VIEW)
        menu.add(path='artist/similar',
                 label=lang(30160),
                 cmd=containerUpdate(url, True))
    # FAVORITES
    wf = node.nt & (~Flag.FAVORITE)
    if node.parent:
        wf = wf and node.parent.nt & ~Flag.FAVORITE
    if wf:
        # ADD TO FAVORITES / TRACKS
        url = node.make_url(nt=Flag.FAVORITE, nm='', mode=Mode.VIEW)
        menu.add(path='favorites',
                 label=c_fav("Favorites"),
                 cmd=containerUpdate(url, True),
                 pos=-9)
        url = node.make_url(
            nt=Flag.FAVORITE,
            nm='gui_add_tracks',
            qid=node.nid,
            qnt=node.nt,
            mode=Mode.VIEW)
        menu.add(path='favorites/add_tracks',
                 label=c_fav(lang(30167) + ' tracks'),
                 cmd=runPlugin(url))
        # ADD TO FAVORITES / Albums
        url = node.make_url(
            nt=Flag.FAVORITE,
            nm='gui_add_albums',
            qid=node.nid,
            qnt=node.nt,
            mode=Mode.VIEW)
        menu.add(path='favorites/add_albums',
                 label=c_fav(lang(30167) + ' albums'),
                 cmd=runPlugin(url))
        # ''' ADD TO FAVORITES / Artists'''
        # url = node.make_url(
        #     nt=Flag.FAVORITE,
        #     nm='gui_add_artists',
        #     qid=node.nid,
        #     qnt=node.nt,
        #     mode=Mode.VIEW)
        # menu.add(path='favorites/add_artists',
        #          label=c_fav(lang(30167) + ' artists'),
        #          cmd=runPlugin(url))

    if node.parent and (node.parent.nt & Flag.FAVORITE):
        url = node.make_url(nt=Flag.FAVORITE, nm='', mode=Mode.VIEW)
        menu.add(path='favorites',
                 label="Favorites",
                 cmd=containerUpdate(url, True),
                 pos=-9)
        url = node.make_url(
            nt=Flag.FAVORITE,
            nm='gui_remove',
            qid=node.nid,
            qnt=node.nt,
            mode=Mode.VIEW)
        menu.add(path='favorites/remove',
                 label=c_fav('Remove %s' % (node.get_label())),
                 cmd=runPlugin(url),
                 color=colorCaution)
    wf = ~Flag.USERPLAYLISTS
    if wf:
        # PLAYLIST
        cmd = containerUpdate(
            node.make_url(
                nt=Flag.USERPLAYLISTS, nid='', mode=Mode.VIEW))
        menu.add(path='playlist',
                 pos=1,
                 label=c_pl("Playlist"),
                 cmd=cmd,
                 mode=Mode.VIEW)
        # ADD TO CURRENT PLAYLIST
        cmd = runPlugin(
            node.make_url(
                nt=Flag.PLAYLIST,
                nm='gui_add_to_current',
                qnt=node.nt,
                mode=Mode.VIEW,
                qid=node.nid))
        menu.add(path='playlist/add_to_current',
                 label=c_pl(lang(30161)),
                 cmd=cmd)
        label = node.get_label()
        try:
            label = label.encode('utf8', 'replace')
        except Exception as e:
            logger.warn('Cannot set query... %s %s', repr(label), e)
            label = ''
        label = urllib.quote_plus(label)
        # ADD AS NEW
        cmd = runPlugin(
            node.make_url(
                nt=Flag.PLAYLIST,
                nm='gui_add_as_new',
                qnt=node.nt,
                query=label,
                mode=Mode.VIEW,
                qid=node.nid))
        menu.add(path='playlist/add_as_new',
                 label=c_pl(lang(30082)),
                 cmd=cmd)
    # PLAYLIST / CREATE
    cFlag = (Flag.PLAYLIST | Flag.USERPLAYLISTS)
    if node.nt | cFlag == cFlag:
        cmd = runPlugin(
            node.make_url(
                nt=Flag.PLAYLIST, nm="gui_create", mode=Mode.VIEW))
        menu.add(path='playlist/create', label=c_pl(lang(30164)), cmd=cmd)
    # VIEW BIG DIR
    # cmd = containerUpdate(node.make_url(mode=Mode.VIEW_BIG_DIR))
    # menu.add(path='qobuz/big_dir', label=lang(30158), cmd=cmd)
    if config.app.registry.get('enable_scan_feature', to='bool'):
        # SCAN
        query = urllib.quote_plus(
            node.make_url(
                mode=Mode.SCAN, asLocalUrl=True))
        url = node.make_url(
            nt=Flag.ROOT, mode=Mode.VIEW, nm='gui_scan', query=query)
        menu.add(path='qobuz/scan', cmd=runPlugin(url), label='scan')
    if node.nt & (Flag.ALL & ~Flag.ALBUM & ~Flag.TRACK & ~Flag.PLAYLIST):
        # ERASE CACHE
        cmd = runPlugin(
            node.make_url(
                nt=Flag.ROOT, nm="cache_remove", mode=Mode.VIEW))
        menu.add(path='qobuz/erase_cache',
                 label=lang(30117),
                 cmd=cmd,
                 color=colorCaution,
                 pos=10)
        if config.app.registry.get('enable_scan_feature', to='bool'):
            # HTTP / Kooli / Ping
            cmd = runPlugin(
                node.make_url(
                    nt=Flag.TESTING, nm="show_dialog", mode=Mode.VIEW))
            menu.add(path='qobuz/test httpd',
                     label='Test web service',
                     cmd=cmd,
                     pos=11)
