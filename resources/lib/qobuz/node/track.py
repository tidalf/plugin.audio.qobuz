'''
    qobuz.node.track
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time
from qobuz.constants import Mode
from qobuz.node import Flag, ErrorNoData
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import lang, getImage, runPlugin, getSetting, containerUpdate
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.theme import theme


class Node_track(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_track, self).__init__(parent=parent,
                                         parameters=parameters,
                                         data=data)
        self.nt = Flag.TRACK
        self.content_type = 'files'
        self.qobuz_context_type = 'playlist'
        self.is_folder = False
        self.status = None
        self.image = getImage('song')
        self.purchased = False

    def fetch(self, xdir, lvl, whiteFlag, blackFlag):
        if blackFlag & Flag.STOPBUILD == Flag.STOPBUILD:
            return None
        return api.get('/track/get', track_id=self.nid)

    def populate(self, xdir, lvl, whiteFlag, blackFlag):
        return xdir.add_node(self)

    def make_local_url(self):
        return '{scheme}://{host}:{port}/qobuz/{album_id}/{nid}/file.mpc'.format(
                scheme='http',
                host=getSetting('httpd_host'),
                port=getSetting('httpd_port'),
                album_id=self.get_album_id(),
                nid=str(self.nid))

    def make_url(self, mode=Mode.PLAY, asLocalUrl=False, **ka):
        if asLocalUrl is True:
            return self.make_local_url()
        purchased = self.get_parameter('purchased')
        if purchased:
            ka['purchased'] = purchased
            self.purchased = True
        return super(Node_track, self).make_url(mode=mode,
                                                asLocalUrl=asLocalUrl,
                                                **ka)

    def get_label(self, fmt="%a - %t", default=None):
        fmt = fmt.replace("%a", self.get_album_artist())
        fmt = fmt.replace("%t", self.get_title())
        fmt = fmt.replace("%A", self.get_album())
        fmt = fmt.replace("%n", str(self.get_track_number()))
        fmt = fmt.replace("%g", self.get_genre())
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
        if self.parent and (self.parent.nt & Flag.ALBUM):
            return self.parent.get_title()
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
        return '%s (albums: %s)' % (label, self.get_property('album/label/albums_count', default=0))

    def get_album_label_id(self, default=None):
        return self.get_property('album/label/id', default=default)


    def get_image(self, size=None, type='front', default=None):
        if size is None:
            size = getSetting('image_default_size')
        if type == 'thumbnail':
            image = self.get_property('album/image/thumbnail', default=None)
            if image is not None:
                return image
        elif type == 'back':
            image = self.get_property('album/image/back', default=None)
            if image is not None:
                return image
        image = self.get_property(['album/image/%s' % (size),
                                  'album/image/large',
                                  'album/image/small',
                                  'album/image/thumbnail'], default=None)
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
        artist = self.get_property(['album/artist/name',
                                    'album/performer/name'], default=None)
        if artist is not None:
            return artist
        if self.parent is not None:
            return self.parent.get_artist()
        return 'n/a'

    def get_artist(self):
        return self.get_property(['artist/name',
                                  'composer/name',
                                  'performer/name',
                                  'interpreter/name',
                                  'composer/name',
                                  'album/artist/name'])

    def get_artist_id(self):
        return self.get_property(['artist/id',
                                  'composer/id',
                                  'performer/id',
                                  'interpreter/id',
                                  'composer/id',
                                  'album/artist/id'], default=None, to='int')

    def get_track_number(self, default=0):
        return self.get_property('track_number', default=default, to='int')

    def get_media_number(self, default=0):
        return self.get_property('media_number', default=default, to='int')

    def get_duration(self):
        duration = self.get_property('duration', default=None)
        if duration is None:
            debug.error(self, "no duration\n%s" % (pprint.pformat(self.data)))
        return duration


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
        if streamable is False:
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

    def get_hires(self):
        return self.get_property('hires')

    def get_purchased(self):
        return self.get_property('purchased')

    def get_description(self, default='n/a'):
        if self.parent and self.parent.nt & Flag.ALBUM == Flag.ALBUM:
            return self.parent.get_description(default=default)
        return default

    def __getFileUrl(self):
        hires = getSetting('hires_enabled', asBool=True)
        format_id = 6 if getSetting('streamtype') == 'flac' else 5
        if hires and self.get_hires():
            format_id = 27
        if self.get_property('purchased') or self.get_parameter('purchased') == '1' or self.purchased:
            intent = "download"
        else:
            intent = "stream"
        data = api.get('/track/getFileUrl', format_id=format_id,
                       track_id=self.nid, user_id=api.user_id, intent=intent)
        if not data:
            debug.warn(self, "Cannot get stream type for track (network problem?)")
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
        for restriction in ['UserUncredentialed', 'TrackRestrictedByPurchaseCredentials']:
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
            debug.warn(self, "Cannot get mime/type for track (restricted track?)")
            return False
        formatId = int(data['format_id'])
        mime = ''
        if formatId in [6, 27]:
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
        return round(min(self.get_property('popularity', to='float',
                                           default=default), 1.0) * 5.0)

    def makeListItem(self, replaceItems=False):
        import xbmcgui  # @UnresolvedImport
        isplayable = 'true'
        item = xbmcgui.ListItem(self.get_label(),
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
        comment = u'''- Label: {label}
- Description: {description}
- Purchasable: {purchasable} / Purchased: {purchased}
- Copyright: {copyright}
- Popularity: {popularity}
- Maximum sampling rate: {maximum_sampling_rate}
- HiRes: {hires} / HiRes purchased: {hires_purchased}
- Streamable: {streamable}
- Previewable: {previewable}
- Sampleable: {sampleable}
- Downloadable: {downloadable}
'''.format(popularity=self.get_property('popularity', default='n/a'),
           label=self.get_album_label(),
            copyright=self.get_property('copyright', default='n/a'),
            maximum_sampling_rate=self.get_property('maximum_sampling_rate'),
            description=self.get_description(),
            hires=self.get_property('hires'),
            sampleable=self.get_property('sampleable'),
            downloadable=self.get_property('downloadable'),
            purchasable=self.get_property('purchasable'),
            purchased=self.get_property('purchased', default=False),
            previewable=self.get_property('previewable'),
            streamable=self.get_property('streamable'),
            hires_purchased=self.get_property('hires_purchased', default=False)
            )

        item.setInfo(type='Music', infoLabels={
                     'count': self.nid,
                     'title': self.get_title(),
                     'album': self.get_album(),
                     'genre': self.get_genre(),
                     'artist': self.get_album_artist(),
                     'tracknumber': self.get_track_number(default=0),
                     'duration': round(self.get_duration()),
                     'year': self.get_year(),
                     'rating': str(self.get_popularity()),
        })
        item.setProperty('album_artist', self.get_album_artist())
        item.setProperty('album_description', comment)
        item.setProperty('album_style', self.get_genre())
        item.setProperty('album_label', self.get_property('album/label/name'))
        item.setProperty('DiscNumber', str(self.get_media_number(default=1)))
        item.setProperty('IsPlayable', isplayable)
        item.setProperty('IsInternetStream', isplayable)
        item.setProperty('Music', isplayable)
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item

    def attach_context_menu(self, item, menu):
        if self.parent and (self.parent.nt & Flag.PLAYLIST == Flag.PLAYLIST):
            url = self.parent.make_url(nt=Flag.PLAYLIST,
                                       nid=self.parent.nid,
                                       qid=self.get_playlist_track_id(),
                                       nm='gui_remove_track',
                                       mode=Mode.VIEW)
            menu.add(path='playlist/remove',
                     label=lang(30075),
                     cmd=runPlugin(url), color=theme.get('item/caution/color'))
        label = self.get_album_label(default=None)
        if label is not None:
            label_id = self.get_album_label_id()
            url = self.make_url(nt=Flag.LABEL, nid=self.get_album_label_id(),
                                mode=Mode.VIEW)
            menu.add(path='label/view', label='View label (i8n): %s' % label,
                     cmd=containerUpdate(url))
        ''' Calling base class '''
        super(Node_track, self).attach_context_menu(item, menu)
