'''
    qobuz.node.inode.props
    ~~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node import Flag
from qobuz.debug import getLogger

logger = getLogger(__name__)

nodeflag_map = {
    'album': Flag.ALBUM,
    'favorite': Flag.FAVORITE,
    'track': Flag.TRACK,
    'playlist': Flag.PLAYLIST
}

nodeimage_map = {
    'album': 'album',
    'image': 'song'
}

nodecontenttype_map = {
    'album': 'songs',
    'track': 'files',
    'playlist': 'albums',
}


def node_name_from_class(cls):
    return cls.__name__.split('.')[-1].replace('Node_', '')


def node_type_from_class(cls):
    try:
        return nodeflag_map[node_name_from_class(cls)]
    except Exception:
        return None


def node_image_from_class(cls):
    try:
        return nodeimage_map[node_name_from_class(cls)]
    except Exception:
        return None


def node_contenttype_from_class(cls):
    try:
        return nodecontenttype_map[node_name_from_class(cls)]
    except Exception:
        return None
