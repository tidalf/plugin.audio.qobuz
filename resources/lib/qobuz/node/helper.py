'''
    qobuz.node.helper
    ~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.debug import getLogger
from qobuz.node import getNode, Flag

logger = getLogger(__name__)


def make_local_track_url(config, track):
    return '{scheme}://{host}:{port}/qobuz/{album_id}/{nid}.mpc'.format(
        scheme='http',
        host=config.app.registry.get('httpd_host'),
        port=config.app.registry.get('httpd_port'),
        album_id=track.get_album_id(),
        nid=str(track.nid))


def make_local_album_url(config, album):
    return '{scheme}://{host}:{port}/qobuz/{album_id}/'.format(
        scheme='http',
        host=config.app.registry.get('httpd_host'),
        port=config.app.registry.get('httpd_port'),
        album_id=album.nid)


class TreeTraverseOpts(object):
    _properties = ['xdir', 'lvl', 'whiteFlag', 'blackFlag', 'noRemote', 'data']

    def __init__(self, **ka):
        self.xdir = None
        self.lvl = None
        self.whiteFlag = None
        self.blackFlag = None
        self.noRemote = False
        self.data = None
        self.parse_keyword_argument(**ka)

    def parse_keyword_argument(self, **ka):
        for key in ka:
            if key not in self._properties:
                raise KeyError(key)
            setattr(self, key, ka.get(key))

    def clone(self):
        return TreeTraverseOpts(**{p: getattr(self, p)
                                   for p in self._properties})


def get_tree_traverse_opts(options=None):
    if options is None:
        return TreeTraverseOpts()
    return options.clone()


def get_node_album(album):
    node = getNode(Flag.ALBUM, data=album)
    cache = node.fetch(TreeTraverseOpts(noRemote=True))
    if cache is not None:
        node.data = cache
    return node
