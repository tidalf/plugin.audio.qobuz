'''
    qobuz.node.track.main
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time

from .props import propsMap
from .context_menu import attach_context_menu
from .list_item import make_list_item

from qobuz import config
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.node import Flag, ErrorNoData
from qobuz.node import helper
from qobuz.node.inode import INode

logger = getLogger(__name__)


class Node_track(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_track, self).__init__(parent=parent,
                                         parameters=parameters,
                                         data=data)
        self._intent = None
        self.is_folder = False
        self.propsMap = propsMap
        self.purchased = False
        self.qobuz_context_type = 'playlist'
        self.status = None

    def fetch(self, xdir=None, lvl=1, whiteFlag=None, blackFlag=None):
        if blackFlag is not None:
            if blackFlag & Flag.STOPBUILD == Flag.STOPBUILD:
                return None
        return api.get('/track/get', track_id=self.nid)

    def populate(self, xdir=None, *a, **ka):
        return xdir.add_node(self)

    def make_local_url(self):
        return helper.make_local_track_url(config, self)

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
        fmt = fmt.replace("%n",
                          str(self.get_track_number())) if '%n' in fmt else fmt
        fmt = fmt.replace("%g", self.get_genre()) if '%g' in fmt else fmt
        return fmt

    def get_label2(self):
        return self.get_artist()

    def get_album(self):
        album = self.get_property('album/title', default=None)
        if album is not None:
            return album
        if self.parent is not None:
            if self.parent.nt & Flag.ALBUM == Flag.ALBUM:
                return self.parent.get_title(default=u'')
        logger.warn('Track without album name: %s',
                    self.get_label())
        return u''

    def get_album_id(self):
        aid = self.get_property('album/id')
        if not aid and self.parent:
            logger.warn('using album id from parent %s', aid)
            return self.parent.nid
        return aid

    def get_album_label(self, default=None):
        label = self.get_property('album/label/name')
        if label is None:
            return default
        return '%s (albums: %s)' % (label, self.get_property(
            'album/label/albums_count', default=0))

    def get_image(self, size=None, img_type='front', default=None):
        if size is None:
            size = config.app.registry.get('image_default_size')
        if img_type == 'thumbnail':
            image = self.get_property('album/image/thumbnail', default=None)
            if image is not None:
                return image
        elif img_type == 'back':
            image = self.get_property('album/image/back', default=None)
            if image is not None:
                return image
        image = self.get_property([
            'album/image/%s' % size, 'album/image/large',
            'album/image/small', 'album/image/thumbnail'
        ], default=None)
        if image is not None:
            return image
        if self.parent and self.parent.nt & (Flag.ALBUM | Flag.PLAYLIST):
            return self.parent.get_image()
        return default

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
            logger.warn('streaming_url, no url returned\n'
                        'API Error: %s' % api.error)
            return None
        return data['url']

    def get_album_artist(self):
        artist = self.get_property(
            ['album/artist/name', 'album/performer/name'], default=None)
        if artist is not None:
            return artist
        try:
            if self.parent is not None:
                return self.parent.get_artist()
        except Exception as e:
            logger.error('NoAlbumArtist: %s', e)
        return 'n/a'

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
            logger.warn('Invalid date format %s, %s', date, e)
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
        format_id, intent, _description = self._intent
        data = api.get('/track/getFileUrl',
                       format_id=format_id,
                       track_id=self.nid,
                       user_id=user.get_id(),
                       intent=intent)
        if not data:
            logger.warn('Cannot get stream type for track (network problem?)')
            return None
        return data

    def get_restrictions(self):
        data = self.__getFileUrl()
        if not data:
            raise ErrorNoData('Cannot get track restrictions')
        restrictions = []
        if 'restrictions' not in data:
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
        if 'format_id' not in data:
            logger.warn('Cannot get mime/type for track (restricted track?)')
            return False
        formatId = int(data['format_id'])
        mime = ''
        if formatId in [6, 27, 7]:
            mime = 'audio/flac'
        elif formatId == 5:
            mime = 'audio/mpeg'
        else:
            logger.warn('Unknow format %s', formatId)
            mime = 'audio/mpeg'
        return mime

    def item_add_playing_property(self, item):
        """ We add this information only when playing item because it require
        us to fetch data from Qobuz
        """
        mime = self.get_mimetype()
        if not mime:
            logger.warn('Cannot set item streaming url')
            return False
        item.setProperty('mimetype', mime)
        item.setPath(self.get_streaming_url())
        return True

    def get_popularity(self, default=0.0):
        return round(
            min(self.get_property(
                'popularity', to='float', default=default),
                1.0) * 5.0)

    def get_articles(self, default=None):
        default = [] if default is None else default
        return [
            '%s (%s%s)' % (a['label'], a['price'], a['currency'])
            for a in self.get_property(
                'album/articles', default=default)
        ]

    def get_awards(self, default=None):
        default = [] if default is None else default
        return [
            a['name'] for a in self.get_property(
                'album/awards', default=default)
        ]

    def makeListItem(self, **ka):
        return make_list_item(self, **ka)

    def attach_context_menu(self, item, menu):
        attach_context_menu(self, item, menu)
        super(Node_track, self).attach_context_menu(item, menu)
