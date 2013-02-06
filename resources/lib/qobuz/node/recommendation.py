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
from qobuz.debug import warn
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
    'null': 'All',
}

class Node_recommendation(INode):
    '''Recommendation node, displaying music ordered by category and genre
    '''
    def __init__(self, parameters = {}):
        super(Node_recommendation, self).__init__(parameters)
        self.kind = Flag.RECOMMENDATION
        self.label = _('Recommendation')
        self.genre_id = self.get_parameter('genre-id')
        self.genre_type = self.get_parameter('genre-type')
        self.image = ''
        self.offset = self.get_parameter('offset') or 0

    def url(self, **ka):
        url = super(Node_recommendation, self).url(**ka)
        if self.genre_type:
            url += '&genre-type=' + str(self.genre_type)
        if self.genre_id:
            url += '&genre-id=' + str(self.genre_id)
        return url

    def myid(self):
        if not self.genre_id or not self.genre_type:
            return None
        return str(self.genre_type) + '-' + str(self.genre_id)

    def fetch(self, renderer=None):
        if not (self.genre_type and self.genre_id):
            return True
        offset = self.offset or 0
        data = api.get('/album/getFeatured',
                                  type=RECOS_TYPE_IDS[int(self.genre_type)],
                                  genre_id=self.genre_id,
                                  limit=api.pagination_limit,
                                  offset=offset)
        if not data:
            warn(self, "Cannot fetch data for recommendation")
            return False
        self.data = data
        return True

    def __populate_type(self):
        ''' Populate type, we don't have genre_type nor genre_id
        '''
        for gtype in RECOS_TYPE_IDS:
            parameters = self.parameters.copy()
            parameters['genre-type'] = gtype
            node = getNode(Flag.RECOMMENDATION, parameters)
            label = '%s / %s' % (self.label, RECOS_TYPES[gtype])
            node.label = label
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
            label = '%s / %s / %s' % (self.label, 
                                      RECOS_TYPES[int(self.genre_type)],
                                     RECOS_GENRES[genre_id])  
            node.label = label 
            self.append(node)
        return True

    def __populate_type_genre(self):
        '''Populate album selected by genre_type and genre_id
        '''
        if not self.data:
            return False
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, self.parameters)
            node.data = album
            self.append(node)
        return True

    def populate(self, renderer=None):
        '''We are populating our node based on genre_type and genre_id
        '''
        if not self.genre_type:
            return self.__populate_type()
        elif not self.genre_id:
            return self.__populate_genre()
        self.content_type = 'albums'
        return self.__populate_type_genre()

