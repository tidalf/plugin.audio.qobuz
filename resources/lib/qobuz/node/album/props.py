'''
    qobuz.node.album.props
    ~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.util import properties
from qobuz.util.converter import Converter

propsMap = {
    'downloadable': {
        'to': properties.bool_converter,
        'default': False,
        'map': ['downloadable']
    },
    'displayable': {
        'to': properties.bool_converter,
        'default': True,
        'map': ['displayable']
    },
    'hires': {
        'to': properties.bool_converter,
        'default': False,
        'map': ['hires']
    },
    'hires_purchased': {
        'to': properties.bool_converter,
        'default': False,
        'map': ['hires_purchased']
    },
    'purchased': {
        'to': properties.bool_converter,
        'default': False,
        'map': ['purchased']
    },
    'purchasable': {
        'to': properties.bool_converter,
        'default': False,
        'map': ['purchasable']
    },
    'sampleable': {
        'to': properties.bool_converter,
        'default': False,
        'map': ['sampleable']
    },
    'streamable': {
        'to': properties.bool_converter,
        'default': False,
        'map': ['streamable']
    },
    'previewable': {
        'to': properties.bool_converter,
        'default': False,
        'map': ['previewable']
    },
    'artist': {
        'to': properties.identity_converter,
        'default': u'UnknowwnArtist',
        'map': ['artist/name', 'interpreter/name', 'composer/name']
    },
    'artist_id': {
        'to': properties.identity_converter,
        'default': u'UnknowwnArtist',
        'map': ['artist/id', 'interpreter/id', 'composer/id']
    },
    'album': {
        'to': properties.identity_converter,
        'default': u'UnknowwnAlbum',
        'map': ['title']
    },
    'title': {
        'to': properties.identity_converter,
        'default': u'UnknowwnAlbum',
        'map': ['title']
    },
    'album_label': {
        'alias': 'label'
    },
    'description': {
        'to': Converter.strip_html,
        'default': u'n/a',
        'map': ['description']
    },
    'maximum_sampling_rate': {
        'to': Converter.float,
        'default': 44,
        'map': ['maximum_sampling_rate']
    },
    'duration': {
        'to': Converter.math_floor,
        'default': None,
        'map': ['duration']
    },
    'genre': {
        'to': properties.identity_converter,
        'default': u'UnknownGenre',
        'map': ['genre/name']
    },
    'label': {
        'to': properties.identity_converter,
        'default': u'UnknownLabel',
        'map': ['label/name']
    },
    'media_count': {
        'to': properties.identity_converter,
        'default': 1,
        'map': ['media_count']
    },
    'purchasable_at': {
        'to': properties.identity_converter,
        'default': None,
        'map': ['purchasable_at']
    },
    'released_at': {
        'to': properties.identity_converter,
        'default': None,
        'map': ['released_at']
    },
    'tracks_count': {
        'to': properties.identity_converter,
        'default': 1,
        'map': ['tracks_count']
    },
    'popularity': {
        'to': properties.identity_converter,
        'default': 0,
        'map': ['popularity']
    },
    'label_albums_count': {
        'to': properties.identity_converter,
        'default': 0,
        'map': ['label_albums_count']
    }
}

informationTemplate = u'''- downloadable: {downloadable}
- hires: {hires}
- previewable: {previewable}
- streamable: {streamable}
- sampleable: {sampleable}
- displayable: {displayable}
- purchasable: {purchasable}
- purchased: {purchased}
- purchasable_at: {purchasable_at}
- hires_purchased: {hires_purchased}
{description}{awards}{articles}
- popularity: {popularity}
- duration: {duration} mn
- media_count: {media_count}
- released_at: {released_at}
- tracks_count: {tracks_count}
- label: {label}
- genre: {genre}
- artist: {artist}
- maximum_sampling_rate: {maximum_sampling_rate}
'''
