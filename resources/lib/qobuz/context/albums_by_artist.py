'''
    qobuz.context.albums_by_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
from os import path as P

base_dir = P.abspath(P.join(P.dirname(__file__), P.pardir))
sys.path.append(P.join(base_dir, P.pardir))

from qobuz.application import Application
from qobuz.gui.util import containerUpdate, executeBuiltin
from qobuz.node import getNode, Flag
from qobuz.plugin import Plugin
from qobuz.util.converter import converter

if __name__ == '__main__':
    app = Application(Plugin('plugin.audio.qobuz'))
    app.bootstrap.init_app()
    tag = sys.listitem.getMusicInfoTag()
    query = converter.quote(tag.getArtist())
    node = getNode(
        Flag.SEARCH, parameters={'search-type': 'artists',
                                 'query': query})
    node.data = node.fetch()
    if node.data is None:
        sys.exit(0)
    query = tag.getArtist().lower().strip()
    artist = None
    for _artist in node.data['artists']['items']:
        name = _artist['name'].lower().strip()
        if name == query:
            artist = _artist
            break
    if artist is None:
        sys.exit(0)
    node = getNode(Flag.ALBUMS_BY_ARTIST, parameters={'nid': artist['id']})
    url = 'plugin://plugin.audio.qobuz/%s' % node.make_url()
    executeBuiltin(containerUpdate(url, False))
