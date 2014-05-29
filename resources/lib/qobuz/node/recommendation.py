# -*- coding: utf-8 -*-
'''
    qobuz.node.recommendation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from qobuz.api import api
from inode import INode
from qobuz.node import getNode, Flag
from qobuz.debug import warn, error
from qobuz.i8n import _

RECOS_TYPE_IDS = {
    1: 'new-releases',
    2: 'press-awards',
    3: 'best-sellers',
    4: 'editor-picks',
    5: 'most-featured'
}

RECOS_TYPES = {
    1: _('News'),
    2: _('Press awards'),
    3: _('Best sellers'),
    4: _('Editor picks'),
    5: _('Most featured'),
}

RECOS_GENRES = {
    2:   _('Blues / Country / Folk'),
    10:  _('Classical'),
    6:   _('Chanson française'),
    59:  _('Historical documents / Litterature / Humor'),
    73:  _('Childs / Karakoke / Ambiance'),
    80:  _('Jazz'),
    64:  _('Techno'),
    91:  _('Movie soundtracks'),
    94:  _('World music'),
    112: _('Pop / Rock'),
    127: _('Rap / HipHop / R&B / Soul'),
    123: _('Reggae'),
    'null': _('All'),
}


class Node_recommendation(INode):
    '''Recommendation node, displaying music ordered by category and genre
    '''
    def __init__(self, parameters={}):
        super(Node_recommendation, self).__init__(parameters)
        self.kind = Flag.RECOMMENDATION
        self.label = _('Recommendation')
        self.genre_id = self.get_parameter('genre-id', delete=True)
        self.genre_type = self.get_parameter('genre-type', delete=True)
        self.image = ''
        self.items_path = 'albums'

    def url(self, **ka):
        if self.genre_type:
            ka['genre-type'] = str(self.genre_type)
        if self.genre_id:
            ka['genre-id'] = str(self.genre_id)
        return super(Node_recommendation, self).url(**ka)

    def myid(self):
        if not self.genre_id or not self.genre_type:
            return None
        return str(self.genre_type) + '-' + str(self.genre_id)

    def fetch(self, renderer=None):
        if not (self.genre_type and self.genre_id):
            return True
        data = api.get('/album/getFeatured',
                                  type=RECOS_TYPE_IDS[int(self.genre_type)],
                                  genre_id=self.genre_id,
                                  limit=api.pagination_limit,
                                  offset=self.offset)
        if not data:
            warn(self, "Cannot fetch data for recommendation")
            return False
        self.data = data
        return True

    def _get_label(self, label, kind='', genre=''):
        if kind:
            kind = ' / %s' % kind  # @ReservedAssignment
        if genre:
            genre = ' / %s' % genre
        return '%s%s%s' % (label, kind, genre)

    def __populate_type(self):
        ''' Populate type, we don't have genre_type nor genre_id
        '''
        for gtype in RECOS_TYPE_IDS:
            parameters = self.parameters.copy()
            parameters['genre-type'] = gtype
            node = getNode(Flag.RECOMMENDATION, parameters)
            node.label = self._get_label(self.get_label(), RECOS_TYPES[gtype])
            self.append(node)
        return True

    def __populate_genre(self):
        '''Populate genre, we have genre_type but no genre_id
        '''
        for genre_id in RECOS_GENRES:
            parameters = self.parameters.copy()
            parameters['genre-type'] = self.genre_type
            parameters['genre-id'] = genre_id
            node = getNode(Flag.RECOMMENDATION, parameters)
            node.label = self._get_label(self.get_label(),
                                         RECOS_TYPES[int(self.genre_type)],
                                         RECOS_GENRES[genre_id])
            self.append(node)
        return True

    def __populate_type_genre(self):
        '''Populate album selected by genre_type and genre_id
        '''
        print "items_path: %s" % self.items_path
#         if self.data is None:
#             warn(self, "Cannot populate genre (no data)")
#             return False
#         print "Data: %s" % self.data
#         if self.items_path not in self.data:
#             warn(self, "Cannot populate genre(No item_path in data)")
#             return False
#         if self.data[self.items_path] is None:
#             warn('Cannot populate genre (empty data)')
#             return False
#         if "items" not in self.data[self.items_path]:
#            warn(self, "Cannot populate genre (No items in data[items_path])")
#             return False
#         if self.data[self.items_path]['items'] is None:
#             warn(self, "Cannot populate genre (items is None)")
#             return False
        try:
            for album in self.data[self.items_path]['items']:
                node = getNode(Flag.ALBUM, self.parameters)
                node.data = album
                self.append(node)
            return True
        except Exception as e:
            error(self, "Cannot populate genre: %s" % e)
        return False

    def populate(self, renderer=None):
        '''We are populating our node based on genre_type and genre_id
        '''
        if not self.genre_type:
            return self.__populate_type()
        elif not self.genre_id:
            return self.__populate_genre()
        self.content_type = 'albums'
        return self.__populate_type_genre()
