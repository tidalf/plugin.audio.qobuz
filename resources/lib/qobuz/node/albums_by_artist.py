'''
    qobuz.node.albums_by_artist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import weakref
from kodi_six import xbmcgui

from qobuz.api import api
from qobuz.debug import getLogger
from qobuz.gui.contextmenu import contextMenu
from qobuz.node import getNode, Flag
from qobuz.node.inode import INode

logger = getLogger(__name__)


class Node_albums_by_artist(INode):
    '''@class Node_product_by_artist:
    '''

    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_albums_by_artist, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.ALBUMS_BY_ARTIST
        self.content_type = 'albums'
        self._items_path = 'albums/items'

    def get_label(self, default=None):
        return self.get_artist()

    def get_image(self):
        image = self.get_property('picture', default=u'')
        image = image.replace('126s', '_')
        return image

    def get_artist(self):
        return self.get_property('name')

    def get_slug(self):
        return self.get_property('slug')

    def get_artist_id(self):
        return self.nid

    def _count(self):
        return len(self.get_property(self._items_path, default=[]))

    def fetch(self, options=None):
        return api.get('/artist/get',
                       artist_id=self.nid,
                       limit=self.limit,
                       offset=self.offset,
                       extra='albums')

    def populate(self, options=None):
        if self.count() == 0:
            return False
        for album in self.get_property(self._items_path):
            for k in ['artist', 'interpreter', 'composer', 'performer']:
                try:
                    if k in self.data['artist']:
                        album[k] = weakref.proxy(self.data['artist'][k])
                except Exception as e:
                    logger.warn('Strange thing happen %s', e)
            self.add_child(getNode(Flag.ALBUM, data=album))
        return True

    def makeListItem(self, **ka):
        replace_items = ka['replaceItems'] if 'replaceItems' in ka else False
        item = xbmcgui.ListItem(
            self.get_label())
        item.setPath(self.make_url())
        image = self.get_image()
        item.setArt({
            'thumb': image,
            'icon': image
        })
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replace_items)
        return item
