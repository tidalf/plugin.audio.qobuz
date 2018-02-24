'''
    qobuz.node.inode_props
    ~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node import Flag
from qobuz.debug import getLogger

logger = getLogger(__name__)

nodeflag_map = {
    'album': Flag.ALBUM,
    'favorite': Flag.FAVORITE,
    'track': Flag.TRACK
}

nodeimage_map = {
    'album': 'album'
}

nodecontenttype_map = {
    'album': 'songs'
}


def node_name_from_class(cls):
    return cls.__name__.split('.')[-1].replace('Node_', '')


def node_type_from_class(cls):
    try:
        return nodeflag_map[node_name_from_class(cls)]
    except Exception as e:
        logger.info(e)
    return None


def node_image_from_class(cls):
    try:
        return nodeimage_map[node_name_from_class(cls)]
    except Exception as e:
        logger.info(e)
    return None


def node_contenttype_from_class(cls):
    try:
        return nodecontenttype_map[node_name_from_class(cls)]
    except Exception as e:
        logger.info(e)
    return None
