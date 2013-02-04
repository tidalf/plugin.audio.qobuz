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
#@todo: qobuz i8n...
from xbmcpy.util import lang, getImage
from qobuz.debug import warn

RECOS_TYPE_IDS = {
    1: 'new-releases',
    2: 'press-awards',
    3: 'best-sellers',
    4: 'editor-picks',
    5: 'most-featured'
}

RECOS_TYPES = {
    1: lang(31084),
    2: lang(31083),
    3: lang(31085),
    4: lang(31086),
    5: lang(31102),
}

RECOS_GENRES = {
    2: lang(31093),
    10: lang(31095),
    6: lang(31090),
    59: lang(31098),
    73: lang(31201),
    80: lang(31089),
    64: lang(31202),
    91: lang(31094),
    94: lang(31092),
    112: lang(31087),
    127: lang(31200),
    123: lang(31203),
    'null': 'All',
}

class Node_recommendation(INode):
    '''Recommendation node, displaying music ordered by category and genre
    '''
    def __init__(self, parameters = {}):
        super(Node_recommendation, self).__init__(parameters)
        self.kind = Flag.RECOMMENDATION
        self.label = lang(30001)
        self.genre_id = self.get_parameter('genre-id')
        self.genre_type = self.get_parameter('genre-type')
        self.image = getImage('album')
        self.offset = self.get_parameter('offset') or 0

    def url(self, **ka):
        url = super(Node_recommendation, self).url()
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
        limit = 100
        data = api.get('/album/getFeatured',
                                  type=RECOS_TYPE_IDS[int(self.genre_type)],
                                  genre_id=self.genre_id,
                                  limit=limit,
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

