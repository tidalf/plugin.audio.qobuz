'''
    qobuz.node.album
    ~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from inode import INode
from qobuz.debug import warn
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.i8n import _
from qobuz.settings import settings

SPECIAL_PURCHASES = ['0000020110926', '0000201011300', '0000020120220',
                     '0000020120221']

class Node_album(INode):
    '''
        @class Node_product:
    '''
    def __init__(self, parameters={}):
        super(Node_album, self).__init__(parameters)
        self.kind = Flag.ALBUM
        self.content_type = 'songs'
        self.is_special_purchase = False
        self.label = _('Album')
        self.imageDefaultSize = settings.get('image_size_default')

    def fetch(self, renderer=None):
        data = api.get('/album/get', album_id=self.nid)
        if not data:
            warn(self, "Cannot fetch product data")
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, self.parameters)
            if not 'image' in track:
                track['image'] = self.get_image()
            node.data = track
            
            self.append(node)
        return len(self.data['tracks']['items'])

    def url(self, **ka):
        return super(Node_album, self).url(**ka)

    '''
    PROPERTIES
    '''
    def get_artist(self):
        return self.get_property(['artist/name',
                               'interpreter/name', 
                               'composer/name'])

    def get_album(self):
        album = self.get_property('name')
        if not album:
            return ''
        return album

    def get_artist_id(self):
        return self.get_property(['artist/id',
                               'interpreter/id',
                              'composer/id'])

    def get_title(self):
        return self.get_property('title')

    def get_image(self, size = None):
        if not size:
            size = self.imageDefaultSize
        return self.get_property(['image/%s' % (size),
                                   'image/large', 
                                   'image/small',
                                   'image/thumbnail'])

    def get_label(self):
        artist = self.get_artist() or 'VA'
        label = '%s - %s' % (artist, self.get_title())
        return label

    def get_genre(self):
        return self.get_property('genre/name')

    def get_year(self):
        import time
        date = self.get_property('released_at')
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except:
            pass
        return year

    def get_description(self):
        return self.get_property('description')
