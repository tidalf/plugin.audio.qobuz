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
'''
    @class Node_artist(Inode): Artist
'''

class Node_artist(INode):

    def __init__(self, parameters={}):
        super(Node_artist, self).__init__(parameters)
        self.kind = Flag.ARTIST
        self.content_type = 'artists'
        self.offset = self.get_parameter('offset') or 0

    def fetch(self, renderer=None):
        data = api.get('/artist/get', artist_id=self.nid, 
                       limit=api.pagination_limit, 
                        offset=self.offset, extra='albums')
        if not data:
            warn(self, "Build-down: Cannot fetch artist data")
            return False
        self.data = data
        return True

    def get_label(self):
        return self.get_property('name')

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

#    def makeListItem(self, replaceItems=False):
#        import xbmcgui
#        image = self.get_image()
#        url = self.make_url()
#        name = self.get_label()
#        item = xbmcgui.ListItem(name,
#                                name,
#                                image,
#                                image,
#                                url)
#        if not item:
#            warn(self, "Error: Cannot make xbmc list item")
#            return None
#        item.setPath(url)
#        item.setInfo('music' , infoLabels={
##            'genre': 'reggae', # self.get_genre(),
##            'year': '2000', # self.get_year(),
#            'artist': self.get_artist(),           
##            'album': self.get_title(),
#            'comment': self.get_description()
##           'Artist_Description': 'coucou'
#        })
#        ctxMenu = contextMenu()
#        self.attach_context_menu(item, ctxMenu)
#        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
#        return item
