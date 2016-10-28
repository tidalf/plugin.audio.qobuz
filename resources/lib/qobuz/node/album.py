'''
    qobuz.node.album
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import getImage, getSetting, htm2xbmc, color
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.node import getNode, Flag

SPECIAL_PURCHASES = ['0000020110926', '0000201011300', '0000020120220',
                     '0000020120221']


class Node_album(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_album, self).__init__(parent=parent,
                                         parameters=parameters,
                                         data=data)
        self.nt = Flag.ALBUM
        self.image = getImage('album')
        self.content_type = 'albums'
        self.is_special_purchase = False
        self.imageDefaultSize = getSetting('image_default_size')

    def get_nid(self):
        return super(Node_album, self).get_nid()

    def set_nid(self, value):
        super(Node_album, self).set_nid(value)
        if value in SPECIAL_PURCHASES:
            self.is_special_purchase = True

    nid = property(get_nid, set_nid)

    def fetch(self, Dir=None, lvl=-1, whiteFlag=None, blackFlag=None):
        return api.get('/album/get', album_id=self.nid)

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for track in self.data['tracks']['items']:
            track.update({
                'album': {
                    'title': self.get_title(),
                    'id': self.nid,
                    'genre': {
                        'name': self.get_genre()
                    },
                    'label': {
                        'name': self.get_album_label(),
                        'albums_count': self.get_property('label/albums_count')
                    },
                    'year': self.get_year(),
                    'artist': {
                        'name': self.get_artist()
                    }
                }
            })
            self.add_child(getNode(Flag.TRACK, data=track))
        return True if len(self.data['tracks']['items']) > 0 else False

    def make_url(self, asLocalUrl=False, **ka):
        purchased = self.get_parameter('purchased')
        if purchased is not None:
            ka['purchased'] = self.get_parameter('purchased')
        if asLocalUrl is True:
            from qobuz.constants import Mode
            ka['mode'] = Mode.SCAN
        return super(Node_album, self).make_url(**ka)

    def makeListItem(self, replaceItems=False):
        import xbmcgui  # @UnresolvedImport
        image = self.get_image()
        item = xbmcgui.ListItem(
            label=self.get_label(),
            label2=self.get_label2(),
            iconImage=self.get_image(),
            thumbnailImage=self.get_image(),
            path=self.make_url(),
        )
        item.setInfo('music', infoLabels={
            'genre': self.get_genre(),
            'year': self.get_year(),
            'artist': self.get_artist(),
            'title': self.get_title(),
            'album': self.get_album(),
            'comment': self.get_description(default=None),
            'duration': self.get_duration(),
            'discnumber': self.get_property('media_count')
        })
        item.setProperty('album_description', self.get_information())
        item.setProperty('album_label', self.get_album_label())
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item

    def get_information(self):
        debug.info(self, '{} popularity: {}', self.get_label().encode('ascii', errors='ignore'), self.get_property('popularity'))
        txt = ''
        description = self.get_description(default=None)
        if description is not None:
            txt += 'description: %s' % description
        return txt

    def get_artist(self):
        return self.get_property(['artist/name',
                                  'interpreter/name',
                                  'composer/name'])

    def get_album(self):
        return self.get_property('title')

    def get_album_label(self):
        return self.get_property('label/name')

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

    def get_label2(self, default=None):
        return self.get_title()

    def get_label(self, default=None):
        rgb = self.get_property('genre/color', default='#00000')
        genre = self.get_property('genre/name', default='n/a')
        artist = self.get_artist() or 'VA'
        return '%s - %s' % (artist, self.get_title()) #, color(rgb, genre))

    def get_genre(self, default=u''):
        return self.get_property('genre/name', default=default)

    def get_year(self):
        date = self.get_property('released_at', default=None)
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except Exception:
            debug.warn(self, 'Invalid date format %s', date)
        return year

    def get_description(self, default='n/a'):
        txt = self.get_property('description', default=None)
        if txt is not None:
            return htm2xbmc(txt)
        return default

    def get_duration(self):
        return self.get_property('duration')
