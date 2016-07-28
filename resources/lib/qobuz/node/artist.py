'''
    qobuz.node.artist
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.debug import warn
from qobuz.gui.util import getSetting
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.node import getNode, Flag


class Node_artist(INode):
    """@class Node_artist(Inode): Artist
    """

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_artist, self).__init__(parent=parent,
                                          parameters=parameters,
                                          data=data)
        self.nt = Flag.ARTIST
        self.set_label(self.get_name())
        self.is_folder = True
        self.slug = ''
        self.content_type = 'artists'

    def hook_post_data(self):
        self.nid = self.get_property('id')
        self.name = self.get_property('name')
        self.image = self.get_image()
        self.slug = self.get_property('slug')
        self.label = self.name

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        limit = getSetting('pagination_limit')
        data = api.get('/artist/get', artist_id=self.nid, limit=limit,
                       offset=self.offset, extra='albums')
        if not data:
            warn(self, "Build-down: Cannot fetch artist data")
            return False
        self.data = data
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        node_artist = getNode(Flag.ARTIST, data=self.data)
        node_artist.label = '[ %s ]' % (node_artist.label)
        if not 'albums' in self.data:
            return True
        for data in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, data=data)
            self.add_child(node)
        return True

        del self._data['tracks']

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

    def makeListItem(self, replaceItems=False):
        import xbmcgui  # @UnresolvedImport
        image = self.get_image()
        url = self.make_url()
        name = self.get_label()
        item = xbmcgui.ListItem(name,
                                name,
                                image,
                                image,
                                url)
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        item.setPath(url)
        item.setInfo('music', infoLabels={
            'artist': self.get_artist(),
            'comment': self.get_description()
        })
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item
