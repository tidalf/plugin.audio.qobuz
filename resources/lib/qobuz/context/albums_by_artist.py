import sys
from os import path as P
import xbmc
from xbmc import log
base_dir = P.abspath(P.join(P.dirname(__file__),P.pardir))
sys.path.append(P.join(base_dir, P.pardir))
from qobuz.node import getNode, Flag
from qobuz.util.converter import converter
from qobuz.plugin import Plugin
from qobuz.application import Application
from qobuz import debug
from qobuz.renderer.xbmc import QobuzXbmcRenderer as renderer
from qobuz.gui.util import runPlugin, containerUpdate, executeBuiltin
from qobuz import config

if __name__ == '__main__':
    app = Application(Plugin('plugin.audio.qobuz'))
    app.bootstrap.init_app()
    tag = sys.listitem.getMusicInfoTag()
    query = converter.quote(tag.getArtist())
    node = getNode(Flag.SEARCH, parameters={'search-type': 'artists',
                                'query': query})
    node.data = node.fetch()
    if node.data is None:
        sys.exit(0)
    query = tag.getArtist().lower().strip()
    artist = None
    for _artist in node.data['artists']['items']:
        a = _artist['name'].lower().strip()
        if a == query:
            artist = _artist
            break
    if artist is None:
        sys.exit(0)
    node = getNode(Flag.ALBUMS_BY_ARTIST, parameters={'nid': artist['id']})
    url = 'plugin://plugin.audio.qobuz/%s' % node.make_url()
    executeBuiltin(containerUpdate(url, False))
