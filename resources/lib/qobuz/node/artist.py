'''
    qobuz.node.artist
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.node import getNode, Flag


class Node_artist(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_artist, self).__init__(parent=parent,
                                          parameters=parameters,
                                          data=data)
        self.nt = Flag.ARTIST
        self.set_label(self.get_name())
        self.content_type = 'artists'

    def hook_post_data(self):
        self.nid = self.get_parameter('nid', default=None) or self.get_property('id', default=None)
        self.name = self.get_property('name')
        self.image = self.get_image()
        self.label = self.name

    def fetch(self, Dir=None, lvl=-1, whiteFlag=None, blackFlag=None):
        return api.get('/artist/get', artist_id=self.nid, extra='albums')

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        node_artist = getNode(Flag.ARTIST, data=self.data)
        node_artist.label = '[ %s ]' % (node_artist.label)
        if 'albums' not in self.data:
            return True
        for data in self.data['albums']['items']:
            self.add_child(getNode(Flag.ALBUM, data=data))
        return True if len(self.data['albums']['items']) > 0 else False

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

    def get_label(self, fmt='%a (%C)'):
        fmt = fmt.replace('%a', self.get_artist())
        fmt = fmt.replace('%G', self.get_genre())
        fmt = fmt.replace('%C', str(self.get_property('albums_count', default=0)))
        return fmt

    def get_title(self):
        return self.get_name()

    def get_artist(self):
        return self.get_name()

    def get_name(self):
        return self.get_property('name')

    def get_genre(self):
        return self.get_property('genre/name', default='n/a')

    def get_owner(self):
        return self.get_property('owner/name')

    def get_description(self):
        return self.get_property('description')

    def makeListItem(self, replaceItems=False):
        import xbmcgui  # @UnresolvedImport
        item = xbmcgui.ListItem(self.get_label(),
                                self.get_label(),
                                self.get_image(),
                                self.get_image(),
                                self.make_url())
        if not item:
            debug.warn(self, 'Error: Cannot make xbmc list item')
            return None
        item.setPath(self.make_url())
        item.setInfo('Music', infoLabels={
            'Artist': self.get_artist(),
            'comment': self.get_description()
        })
        item.setProperty('AlbumArtist', self.get_artist())
        item.setProperty('Album_Genre', self.get_genre())
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item
