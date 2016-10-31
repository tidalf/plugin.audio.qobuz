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
from qobuz.gui.util import getImage, color
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz import config

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
        self.imageDefaultSize = config.app.registry.get('image_default_size')

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
        return u'''{description}
- popularity: {popularity}
- duration: {duration} mn
- previewable: {previewable}
- streamable: {streamable}
- media_count: {media_count}
- purchasable: {purchasable}
- released_at: {released_at}
- tracks_count: {tracks_count}
- displayable: {displayable}
- label: {label}
- downloadable: {downloadable}
- hires: {hires}
- sampleable: {sampleable}
- awards: {awards}
- genre: {genre}
- articles: {articles}
- artist: {artist}
- maximum_sampling_rate: {maximum_sampling_rate}
        '''.format(popularity=self.get_property('popularity'),
                   description=self.get_property('description', default=self.get_label()),
                   duration=round(self.get_property('duration', default=0.0) / 60.0, 2),
                   previewable=self.get_property('previewable'),
                   streamable=self.get_property('streamable'),
                   media_count=self.get_property('media_count'),
                   purchasable=self.get_property('purchasable'),
                   released_at=self.get_property('released_at'),
                   tracks_count=self.get_property('tracks_count'),
                   displayable=self.get_property('displayable'),
                   label=self.get_property('label/name'),
                   downloadable=self.get_property('downloadable'),
                   hires=self.get_property('hires'),
                   sampleable=self.get_property('sampleable'),
                   awards=','.join([a['name'] for a in self.get_property('awards', default=[])]),
                   genre=self.get_property('genre/name'),
                   articles='|'.join(['%s (%s%s)' % (a['label'], a['price'], a['currency']) for a in self.get_property('articles', default=[])]),
                   artist=self.get_artist(),
                   maximum_sampling_rate=self.get_property('maximum_sampling_rate'))

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
        return self.get_property('description', default=None, to='htm2xbmc')

    def get_duration(self):
        return self.get_property('duration', default=None, to='math_floor')
