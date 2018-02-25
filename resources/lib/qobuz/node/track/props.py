'''
    qobuz.node.track.props
    ~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.util import properties
from qobuz.util.converter import Converter

propsMap = {
    'composer': {
        'to': properties.identity_converter,
        'default': -1,
        'map': ['composer/name']
    },
    'interpreter': {
        'to': properties.identity_converter,
        'default': -1,
        'map': ['performer/name']
    },
    'album_label_id': {
        'to': properties.identity_converter,
        'default': None,
        'map': ['album/label/id']
    },
    'playlist_track_id': {
        'to': properties.identity_converter,
        'default': None,
        'map': ['playlist_track_id']
    },
    'position': {
        'to': properties.identity_converter,
        'default': None,
        'map': ['position']
    },
    'title': {
        'to': properties.identity_converter,
        'default': None,
        'map': ['title']
    },
    'artist': {
        'to': properties.identity_converter,
        'default': None,
        'map': [
            'artist/name', 'composer/name', 'performer/name',
            'interpreter/name', 'composer/name', 'album/artist/name'
        ]
    },
    'artist_id': {
        'to': Converter.int,
        'default': None,
        'map': [
            'artist/id', 'composer/id', 'performer/id', 'interpreter/id',
            'composer/id', 'album/artist/id'
        ]
    },
    'track_number': {
        'to': Converter.int,
        'default': 0,
        'map': ['track_number']
    },
    'media_number': {
        'to': Converter.int,
        'default': 0,
        'map': ['media_number']
    },
    'streamable': {
        'to': Converter.bool,
        'default': False,
        'map': ['streamable']
    },
    'sampleable': {
        'to': Converter.bool,
        'default': False,
        'map': ['sampleable']
    },
    'hires': {
        'to': Converter.bool,
        'default': False,
        'map': ['hires']
    },
    'hires_purchased': {
        'to': Converter.bool,
        'default': False,
        'map': ['hires_purchased']
    },
    'purchased': {
        'to': Converter.bool,
        'default': False,
        'map': ['purchased']
    },
    'purchasable': {
        'to': Converter.bool,
        'default': False,
        'map': ['purchasable']
    },
    'maximum_bit_depth': {
        'to': Converter.float,
        'default': 44.4,
        'map': ['maximum_bit_depth']
    },
    'maximum_sampling_rate': {
        'to': Converter.float,
        'default': 44.4,
        'map': ['maximum_sampling_rate']
    },
    'displayable': {
        'to': Converter.bool,
        'default': False,
        'map': ['displayable']
    },
    'downloadable': {
        'to': Converter.bool,
        'default': False,
        'map': ['downloadable']
    },
    'previewable': {
        'to': Converter.bool,
        'default': False,
        'map': ['previewable']
    }
}
