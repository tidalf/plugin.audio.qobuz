'''
    qobuz.node.playlist.props
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.util import properties

propsMap = {
    'name': {
        'to': properties.identity_converter,
        'default': 'UnknownPlaylistName',
        'map': ['name', 'title']
    },
    'owner': {
        'to': properties.identity_converter,
        'default': 'UnknownPlaylistOwnerName',
        'map': ['owner/name']
    },
    'owner_id': {
        'to': properties.identity_converter,
        'default': 'UnknownPlaylistOwnerId',
        'map': ['owner/id']
    },
    'description': {
        'to': properties.identity_converter,
        'default': 'UnknownPlaylistOwnerId',
        'map': ['description']
    },
}
