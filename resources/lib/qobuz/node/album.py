'''
    qobuz.node.album
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.debug import warn, info
from qobuz.gui.util import getImage, getSetting, htm2xbmc
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.node import getNode, Flag

SPECIAL_PURCHASES = ['0000020110926', '0000201011300', '0000020120220',
                     '0000020120221']


class Node_album(INode):
    """@class Node_product:
    """

    def __init__(self, parent, params):
        super(Node_album, self).__init__(parent, params)
        self.nt = Flag.ALBUM
        self.image = getImage('album')
        self.content_type = 'songs'
        self.is_special_purchase = False
        self.imageDefaultSize = 'large'
        self.label = 'Album'
        self.offset = self.get_parameter('offset') or 0
        try:
            self.imageDefaultSize = getSetting('image_default_size')
        except Exception as e:
            warn(self, 'Cannot set image default size, Error: {}', e)

    def get_nid(self):
        return super(Node_album, self).get_nid()

    def set_nid(self, value):
        super(Node_album, self).set_nid(value)
        if value in SPECIAL_PURCHASES:
            self.is_special_purchase = True

    nid = property(get_nid, set_nid)

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        data = api.get('/album/get', album_id=self.nid)
        if not data:
            warn(self, "Cannot fetch product data")
            return False
        self.data = data
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, data=track)
            if 'image' not in track:
                track['image'] = self.get_image()
            self.add_child(node)
        return len(self.data['tracks']['items'])

    def make_url(self, **ka):
        purchased = self.get_parameter('purchased')
        if purchased is not None:
            ka['purchased'] = self.get_parameter('purchased')
        if 'asLocalURL' in ka and ka['asLocalURL'] == 'True':
            from constants import Mode
            ka['mode'] = Mode.SCAN
        return super(Node_album, self).make_url(**ka)

    def makeListItem(self, replaceItems=False):
        import xbmcgui  # @UnresolvedImport
        image = self.get_image()
        item = xbmcgui.ListItem(
            label=self.get_label(),
            label2=self.get_label2(),
            iconImage=image,
            thumbnailImage=image,
            path=self.make_url(),
        )
        item.setInfo('music', infoLabels={
            'genre': self.get_genre(),
            'year': self.get_year(),
            'artist': self.get_artist(),
            'title': self.get_title(),
            'album': self.get_title(),
            'comment': self.get_description()
        })
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item

    """
    PROPERTIES
    """

    def get_artist(self):
        return self.get_property(['artist/name',
                                  'interpreter/name',
                                  'composer/name'])

    def get_album(self):
        return self.get_property('name')

    def get_artist_id(self):
        return self.get_property(['artist/id',
                                  'interpreter/id',
                                  'composer/id'])

    def get_title(self):
        return self.get_property('title')

    def get_image(self, size=None):
        if not size:
            size = self.imageDefaultSize
        return self.get_property(['image/%s' % (size),
                                  'image/large',
                                  'image/small',
                                  'image/thumbnail'])

    def get_label(self):
        artist = self.get_artist() or 'VA'
        return '%s - %s' % (artist, self.get_title())

    def get_genre(self):
        return self.get_property('genre/name')

    def get_year(self):
        import time
        date = self.get_property('released_at', default=None)
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except Exception:
            warn(self, 'Invalid date format %s', date)
        return year

    def get_description(self):
        return htm2xbmc(self.get_property('description'))
