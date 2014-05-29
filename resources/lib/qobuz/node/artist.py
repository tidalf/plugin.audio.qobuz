'''
    qobuz.node.artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.debug import warn
from qobuz.i8n import _


class Node_artist(INode):
    '''
        @class Node_artist(Inode): Artist
    '''

    def __init__(self, parameters={}):
        super(Node_artist, self).__init__(parameters)
        self.kind = Flag.ARTIST
        self.content_type = 'artists'
        self.add_action('similar',
                        label=_('Similar artists'),
                        target=Flag.ARTIST_SIMILAR)
        self.add_action('featured',
                        label=_('Featured album'),
                        target=Flag.ALBUMS_BY_ARTIST)

    def fetch(self, renderer=None):
        data = api.get('/artist/get', artist_id=self.nid,
                       limit=api.pagination_limit,
                        offset=self.offset, extra='albums')
        if not data:
            warn(self, "Build-down: Cannot fetch artist data")
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        node_artist = getNode(Flag.ARTIST, self.parameters)
        node_artist.data = self.data
        node_artist.label = '[ %s ]' % (node_artist.label)
        if not 'albums' in self.data:
            return True
        for pData in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, self.parameters)
            node.data = pData
            self.append(node)
        return True

    def get_label(self):
        return self.get_property('name')

    def get_artist_id(self):
        return self.nid

    def get_image(self):
        image = self.get_property(['image/extralarge',
                                   'image/mega',
                                   'image/large',
                                   'image/medium',
                                   'image/small',
                                   'picture'])
        if image:
            image = image.replace('126s', '_')
        return image

    def get_title(self):
        return self.get_name()

    def get_artist(self):
        return self.get_name()

    def get_name(self):
        return self.get_property('name')

    def get_owner(self):
        return self.get_property('owner/name')

    def get_description(self):
        return self.get_property('description')
