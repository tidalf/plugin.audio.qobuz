'''
    qobuz.node.artist
    ~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from kodi_six import xbmcgui  # pylint:disable=E0401

from qobuz.api import api
from qobuz.debug import getLogger
from qobuz.gui.contextmenu import contextMenu
from qobuz.gui.util import getImage
from qobuz.node import Flag, helper
from qobuz.node.inode import INode
from qobuz.util import properties
logger = getLogger(__name__)


propsMap = {
    'name': {
        'to': properties.identity_converter,
        'default': 'UnknownArtists',
        'map': ['name']
    },
    'artist': {
        'alias': 'name'
    },
    'title': {
        'alias': 'name'
    },
    'image': {
        'to': properties.identity_converter,
        'default': getImage('artists'),
        'map': [
            'image/extralarge',
            'image/mega',
            'image/large',
            'image/medium',
            'image/small',
            'picture'
        ]
    },
    'owner': {
        'to': properties.identity_converter,
        'default': 'UnknownOwner',
        'map': ['owner/name']
    },
    'description': {
        'to': properties.strip_html_converter,
        'default': '',
        'map': ['biography/content']
    }
}


def helper_album_list_genre(data, default=None):
    default = [] if default is None else default
    if data is None or 'albums' not in data:
        return default
    genres = {}
    for album in data['albums']['items']:
        if 'genre' not in album:
            continue
        genres[album['genre']['name']] = 1
    return genres.keys()


class Node_artist(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_artist, self).__init__(parent=parent,
                                          parameters=parameters,
                                          data=data)
        self.nt = Flag.ARTIST
        self.content_type = 'artists'
        self.propsMap = propsMap

    def fetch(self, options=None):
        if options and options.noRemote:
            return self.data
        return api.get('/artist/get', artist_id=self.nid, extra='albums')

    def populate(self, options=None):
        albums = self.get_property('albums/items')
        if not albums:
            return False
        for album in albums:
            node = helper.get_node_album(album)
            self.add_child(node)
        return True

    def get_artist_id(self):
        ''' Return artist nid'''
        return self.nid

    def get_label(self, default=None):
        if self.data is None:
            return 'UnknownArtist'
        fmt = '%a (%C)'
        fmt = fmt.replace(
            '%Cc',
            self.get_property('albums_as_primary_composer_count',
                              default='0',
                              to='string'))
        fmt = fmt.replace(
            '%Ca',
            self.get_property(
                'albums_as_primary_artist_count',
                default='0',
                to='string'))
        fmt = fmt.replace('%a', self.get_artist())
        fmt = fmt.replace('%G', self.get_genre())
        fmt = fmt.replace(
            '%C', str(self.get_property(
                'albums_count', default=0)))
        return fmt

    def get_genre(self):
        '''Return comma separated genres for this artist'''
        return ', '.join(helper_album_list_genre(self.data))

    def makeListItem(self, **ka):
        replace_items = ka['replaceItems'] if 'replaceItems' in ka else False
        genre = self.get_genre()
        image = str(self.get_image())
        logger.info('image %s', image)
        label = self.get_label()
        item = xbmcgui.ListItem(label)
        item.setPath(self.make_url())
        item.setArt({
            'thumb': image,
            'icon': image
        })
        item.setInfo(
            'Music',
            infoLabels={
                'artist': self.get_artist(),
                'genre': genre,
                'comment': self.get_description()
            })
        ctx_menu = contextMenu()
        self.attach_context_menu(item, ctx_menu)
        item.addContextMenuItems(ctx_menu.getTuples(), replace_items)
        return item
