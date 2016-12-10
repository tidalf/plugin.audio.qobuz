'''
    qobuz.node.track
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time
import xbmcgui

from qobuz.constants import Mode
from qobuz.node import Flag, ErrorNoData
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import lang, getImage, runPlugin, containerUpdate
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.theme import theme
from qobuz import config


class Node_track(INode):
    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_track, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.TRACK
        self.content_type = 'files'
        self.qobuz_context_type = 'playlist'
        self.is_folder = False
        self.status = None
        self.image = getImage('song')
        self.purchased = False
        self._intent = None

    def fetch(self, xdir=None, lvl=1, whiteFlag=None, blackFlag=None):
        if blackFlag is not None and blackFlag & Flag.STOPBUILD == Flag.STOPBUILD:
            return None
        return api.get('/track/get', track_id=self.nid)

    def populate(self, xdir=None, *a, **ka):
        return xdir.add_node(self)

    def make_local_url(self):
        return '{scheme}://{host}:{port}/qobuz/{album_id}/{nid}/file.mpc'.format(
            scheme='http',
            host=config.app.registry.get('httpd_host'),
            port=config.app.registry.get('httpd_port'),
            album_id=self.get_album_id(),
            nid=str(self.nid))

    def make_url(self, mode=Mode.PLAY, asLocalUrl=False, **ka):
        if asLocalUrl is True:
            return self.make_local_url()
        purchased = self.get_parameter('purchased')
        if purchased:
            ka['purchased'] = purchased
            self.purchased = True
        return super(Node_track, self).make_url(mode=mode, **ka)

    def get_label(self, fmt="%a - %t", default=None):
        fmt = fmt.replace("%a", self.get_artist()) if '%a' in fmt else fmt
        fmt = fmt.replace("%A",
                          self.get_album_artist()) if '%A' in fmt else fmt
        fmt = fmt.replace("%t", self.get_title()) if '%t' in fmt else fmt
        #fmt = fmt.replace("%A", self.get_album())
        fmt = fmt.replace("%n",
                          str(self.get_track_number())) if '%n' in fmt else fmt
        fmt = fmt.replace("%g", self.get_genre()) if '%g' in fmt else fmt
        return fmt

    def get_label2(self):
        return self.get_artist()

    def get_composer(self):
        return self.get_property('composer/name', default=-1)

    def get_interpreter(self):
        return self.get_property('performer/name', default=-1)

    def get_album(self):
        album = self.get_property('album/title', default=None)
        if album is not None:
            return album
        if self.parent is not None and self.parent.nt & Flag.ALBUM == Flag.ALBUM:
            return self.parent.get_title(default=u'')
        debug.warn(self, 'Track without album name: {}', self.get_label())
        return u''

    def get_album_id(self):
        aid = self.get_property('album/id')
        if not aid and self.parent:
            return self.parent.nid
        return aid

    def get_album_label(self, default=None):
        label = self.get_property('album/label/name')
        if label is None:
            return default
        return '%s (albums: %s)' % (label, self.get_property(
            'album/label/albums_count', default=0))

    def get_album_label_id(self, default=None):
        return self.get_property('album/label/id', default=default)

    def get_image(self, size=None, type='front', default=None):
        if size is None:
            size = config.app.registry.get('image_default_size')
        if type == 'thumbnail':
            image = self.get_property('album/image/thumbnail', default=None)
            if image is not None:
                return image
        elif type == 'back':
            image = self.get_property('album/image/back', default=None)
            if image is not None:
                return image
        image = self.get_property(
            [
                'album/image/%s' % (size), 'album/image/large',
                'album/image/small', 'album/image/thumbnail'
            ],
            default=None)
        if image is not None:
            return image
        if self.parent and self.parent.nt & (Flag.ALBUM | Flag.PLAYLIST):
            return self.parent.get_image()
        return default

    def get_playlist_track_id(self):
        return self.get_property('playlist_track_id')

    def get_position(self):
        return self.get_property('position')

    def get_title(self):
        return self.get_property('title')

    def get_genre(self):
        genre = self.get_property('album/genre/name', default=None)
        if genre is not None:
            return genre
        if self.parent is not None:
            return self.parent.get_genre()
        return u''

    def get_streaming_url(self):
        data = self.__getFileUrl()
        if not data:
            return None
        if 'url' not in data:
            debug.warn(self, "streaming_url, no url returned\n"
                       "API Error: %s" % (api.error))
            return None
        return data['url']

    def get_album_artist(self):
        artist = self.get_property(
            ['album/artist/name', 'album/performer/name'], default=None)
        if artist is not None:
            return artist
        if self.parent is not None:
            return self.parent.get_artist()
        return 'n/a'

    def get_artist(self):
        return self.get_property([
            'artist/name', 'composer/name', 'performer/name',
            'interpreter/name', 'composer/name', 'album/artist/name'
        ])

    def get_artist_id(self):
        return self.get_property(
            [
                'artist/id', 'composer/id', 'performer/id', 'interpreter/id',
                'composer/id', 'album/artist/id'
            ],
            default=None,
            to='int')

    def get_track_number(self, default=0):
        return self.get_property('track_number', default=default, to='int')

    def get_media_number(self, default=0):
        return self.get_property('media_number', default=default, to='int')

    def get_duration(self):
        return round(self.get_property('duration', default=0.0) / 60.0, 2)

    def get_year(self):
        date = self.get_property('album/year')
        if date is not None:
            return date
        date = self.get_property('album/released_at', default=None)
        if date is None:
            if self.parent is not None and self.parent.nt & Flag.ALBUM:
                return self.parent.get_year()
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except Exception as e:
            debug.warn(self, 'Invalid date format %s', date)
        return year

    def is_playable(self):
        streamable = self.get_property('streamable', default=None)
        if streamable is False and not user.is_free_account():
            return False
        url = self.get_streaming_url()
        if not url:
            return False
        restrictions = self.get_restrictions()
        if 'TrackUnavailable' in restrictions:
            return False
        if 'AlbumUnavailable' in restrictions:
            return False
        return True

    def get_downloadable(self):
        return self.get_property('downloadable', to='bool', default=False)

    def get_hires(self):
        return self.get_property('hires', to='bool', default=False)

    def get_purchased(self):
        return self.get_property('purchased', to='bool', default=False)

    def get_hires_purchased(self):
        return self.get_property('purchased', to='bool', default=False)

    def get_description(self, default='n/a'):
        description = self.get_property(
            'album/description', default=None, to='strip_html')
        if description is not None:
            return description
        if self.parent and self.parent.nt & Flag.ALBUM == Flag.ALBUM:
            return self.parent.get_description(default=default)
        return default

    def __getFileUrl(self):
        if self._intent is None:
            self._intent = user.stream_format(track=self)
        format_id, intent, description = self._intent
        data = api.get('/track/getFileUrl',
                       format_id=format_id,
                       track_id=self.nid,
                       user_id=user.get_id(),
                       intent=intent)
        if not data:
            debug.warn(self,
                       "Cannot get stream type for track (network problem?)")
            return None
        return data

    def get_restrictions(self):
        data = self.__getFileUrl()
        if not data:
            raise ErrorNoData('Cannot get track restrictions')
        restrictions = []
        if not 'restrictions' in data:
            return restrictions
        for restriction in data['restrictions']:
            restrictions.append(restriction['code'])
        return restrictions

    def is_uncredentialed(self):
        for restriction in [
                'UserUncredentialed', 'TrackRestrictedByPurchaseCredentials'
        ]:
            if restriction in self.get_restrictions():
                return True
        return False

    def is_sample(self):
        data = self.__getFileUrl()
        if not data:
            return False
        if self.is_uncredentialed():
            return True
        if 'sample' in data:
            return data['sample']
        return False

    def get_mimetype(self):
        data = self.__getFileUrl()
        if not data:
            return False
        if not 'format_id' in data:
            debug.warn(self,
                       "Cannot get mime/type for track (restricted track?)")
            return False
        formatId = int(data['format_id'])
        mime = ''
        if formatId in [6, 27, 7]:
            mime = 'audio/flac'
        elif formatId == 5:
            mime = 'audio/mpeg'
        else:
            debug.warn(self, "Unknow format " + str(formatId))
            mime = 'audio/mpeg'
        return mime

    def item_add_playing_property(self, item):
        """ We add this information only when playing item because it require
        us to fetch data from Qobuz
        """
        mime = self.get_mimetype()
        if not mime:
            debug.warn(self, "Cannot set item streaming url")
            return False
        item.setProperty('mimetype', mime)
        item.setPath(self.get_streaming_url())
        return True

    def get_popularity(self, default=0.0):
        return round(
            min(self.get_property(
                'popularity', to='float', default=default),
                1.0) * 5.0)

    def get_streamable(self):
        return self.get_property('streamable', to='bool', default=False)

    def get_articles(self, default=[]):
        return [
            '%s (%s%s)' % (a['label'], a['price'], a['currency'])
            for a in self.get_property(
                'album/articles', default=default)
        ]

    def get_awards(self, default=[]):
        return [
            a['name'] for a in self.get_property(
                'album/awards', default=default)
        ]

    def get_displayable(self):
        return self.get_property('displayable', to='bool', default=False)

    def makeListItem(self, replaceItems=False):
        isplayable = 'true'
        item = xbmcgui.ListItem(
            self.get_label(),
            self.get_label2(),
            self.get_image(),
            self.get_image(type='back'),
            self.make_url(mode=Mode.PLAY))
        if not item:
            debug.warn(self, "Cannot create xbmc list item")
            return None
        item.setArt({
            'thumb': self.get_image(),
            'icon': self.get_image(type='thumbnail')
        })
        comment = u'''- HiRes: {hires}
- HiRes purchased: {hires_purchased}
- purchasable: {purchasable}
- purchased: {purchased}
- streamable: {streamable}
- previewable: {previewable}
- sampleable: {sampleable}
- downloadable: {downloadable}
{description}
- label: {label}
- duration: {duration} mn
- track number: {track_number}
- year: {year}
- composer: {composer}
- performer: {performer}
- copyright: {copyright}
- popularity: {popularity}
- maximum sampling rate: {maximum_sampling_rate}
- maximum_bit_depth: {maximum_bit_depth}
'''.format(
            popularity=self.get_property(
                'popularity', default='n/a'),
            duration=self.get_duration(),
            label=self.get_album_label(),
            year=self.get_property('album/year'),
            performers=self.get_property('performers'),
            track_number=self.get_property('track_number'),
            version=self.get_property('version'),
            performer=self.get_property('performer/name'),
            composer=self.get_property('composer/name'),
            copyright=self.get_property(
                'copyright', default='n/a'),
            maximum_sampling_rate=self.get_maximum_sampling_rate(),
            maximum_bit_depth=self.get_property('maximum_bit_depth'),
            description=self.get_description(default=self.get_label()),
            hires=self.get_property('hires'),
            sampleable=self.get_property('sampleable'),
            downloadable=self.get_downloadable(),
            purchasable=self.get_property('purchasable'),
            purchased=self.get_property(
                'purchased', default=False),
            previewable=self.get_property('previewable'),
            streamable=self.get_streamable(),
            hires_purchased=self.get_property(
                'hires_purchased', default=False),
            awards=','.join(self.get_awards()),
            articles=', '.join(self.get_articles()))

        item.setInfo(
            type='Music',
            infoLabels={
                'count': self.nid,
                'title': self.get_title(),
                'album': self.get_album(),
                'genre': self.get_genre(),
                'artist': self.get_album_artist(),
                'tracknumber': self.get_track_number(default=0),
                'duration': self.get_property('duration'),
                'year': self.get_year(),
                'rating': str(self.get_popularity()),
            })
        item.setProperty('album_artist', self.get_album_artist())
        item.setProperty('album_description', comment)
        item.setProperty('album_label', self.get_property('album/label/name'))
        item.setProperty('Role.Composer', self.get_property('composer/name'))
        item.setProperty('DiscNumber', str(self.get_media_number(default=1)))
        item.setProperty('IsPlayable', isplayable)
        item.setProperty('IsInternetStream', isplayable)
        item.setProperty('Music', isplayable)
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item

    def get_maximum_sampling_rate(self):
        return self.get_property('maximum_sampling_rate')

    def attach_context_menu(self, item, menu):
        if self.parent and (self.parent.nt & Flag.PLAYLIST == Flag.PLAYLIST):
            url = self.parent.make_url(
                nt=Flag.PLAYLIST,
                nid=self.parent.nid,
                qid=self.get_playlist_track_id(),
                nm='gui_remove_track',
                mode=Mode.VIEW)
            menu.add(path='playlist/remove',
                     label=lang(30075),
                     cmd=runPlugin(url),
                     color=theme.get('item/caution/color'))
        label = self.get_album_label(default=None)
        if label is not None:
            label_id = self.get_album_label_id()
            url = self.make_url(
                nt=Flag.LABEL, nid=self.get_album_label_id(), mode=Mode.VIEW)
            menu.add(path='label/view',
                     label='View label (i8n): %s' % label,
                     cmd=containerUpdate(url))
        ''' Calling base class '''
        super(Node_track, self).attach_context_menu(item, menu)
