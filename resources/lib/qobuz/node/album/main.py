'''
    qobuz.node.album.main
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time
from kodi_six import xbmcgui  # pylint:disable=E0401

from .props import propsMap, informationTemplate
from qobuz import config
from qobuz.api import api
from qobuz.debug import getLogger
from qobuz.gui.contextmenu import contextMenu
from qobuz.gui.util import getImage
from qobuz.node import getNode, Flag, helper
from qobuz.node.inode import INode

logger = getLogger(__name__)


class Node_album(INode):

    def __init__(self,
                 parent=None,
                 parameters=None,
                 data=None):
        parameters = parameters if parameters is not None else {}
        super(Node_album, self).__init__(
            parent=parent,
            parameters=parameters,
            data=data)
        self.imageDefaultSize = config.app.registry.get('image_default_size')
        self._items_path = 'tracks/items'
        self.propsMap = propsMap

    def _count(self):
        return len(self.get_property(self._items_path, default=[]))

    def fetch(self, options=None):
        options = helper.get_tree_traverse_opts(options)
        return api.get('/album/get',
                       album_id=self.nid,
                       noRemote=options.noRemote)

    def populate(self, options=None):
        if self.count() == 0:
            return False
        for track in self.get_property(self._items_path):
            track.update({
                'album': {
                    'title': self.get_title(),
                    'id': self.nid,
                    'genre': {
                        'name': self.get_genre()
                    },
                    'label': {
                        'name': self.get_label(),
                        'albums_count': self.get_label_albums_count()
                    },
                    'year': self.get_year(),
                    'artist': {
                        'name': self.get_artist()
                    }
                }
            })
            self.add_child(getNode(Flag.TRACK, data=track))
        return True

    def make_local_url(self):
        return helper.make_local_album_url(config, self)

    def make_url(self, asLocalUrl=False, **ka):
        purchased = self.get_parameter('purchased')
        if purchased is not None:
            ka['purchased'] = self.get_parameter('purchased')
        if asLocalUrl is True:
            from qobuz.constants import Mode
            ka['mode'] = Mode.SCAN
        return super(Node_album, self).make_url(**ka)

    def makeListItem(self, replaceItems=False):
        item = xbmcgui.ListItem(
            label=self.get_label(),
            label2=self.get_label2(),
            iconImage=self.get_image(),
            thumbnailImage=self.get_image(),
            path=self.make_url(), )
        item.setInfo(
            'music',
            infoLabels={
                'genre': self.get_genre(),
                'year': self.get_year(),
                'artist': self.get_artist(),
                'title': self.get_title(),
                'album': self.get_album(),
                'comment': self.get_description(default=None),
                'duration': self.get_duration(),
                'discnumber': self.get_media_count()
            })
        item.setProperty('album_description', self.get_information())
        item.setProperty('album_label', self.get_album_label())
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item

    def get_articles(self, default=None):
        default = [] if default is None else default
        articles = self.get_property('articles', default=None)
        if articles is None:
            return default
        return [
            '%s (%s %s)' % (a['label'], a['price'], a['currency'])
            for a in articles
        ]

    def get_awards(self, default=None):
        default = [] if default is None else default
        awards = self.get_property('awards', default=None)
        if awards is None:
            return default
        return [a['name'] for a in awards]

    def get_information(self):
        awards = self.get_awards(default=None)
        if awards is not None:
            awards = u'\n- awards: %s' % ', '.join(awards)
        else:
            awards = u''
        articles = self.get_articles(default=None)
        if articles is not None:
            articles = u'\n- articles %s' % ', '.join(articles)
        else:
            articles = u''
        duration = round(self.get_property('duration', default=0.0) / 60.0, 2)
        description = self.get_description(default=self.get_label())
        return informationTemplate.format(
            popularity=self.get_popularity(),
            description=description,
            duration=duration,
            previewable=self.get_previewable(),
            streamable=self.get_streamable(),
            media_count=self.get_media_count(),
            purchased=self.get_purchased(),
            purchasable=self.get_purchasable(),
            purchasable_at=self.get_purchasable_at(),
            released_at=self.get_released_at(),
            tracks_count=self.get_tracks_count(),
            displayable=self.get_displayable(),
            label=self.get_label(),
            downloadable=self.get_downloadable(),
            hires=self.get_hires(),
            hires_purchased=self.get_hires_purchased(),
            sampleable=self.get_sampleable(),
            awards=awards,
            genre=self.get_genre(),
            articles=articles,
            artist=self.get_artist(),
            maximum_sampling_rate=self.get_maximum_sampling_rate())

    def get_image(self, size=None):
        if not size:
            size = self.imageDefaultSize
        return self.get_property([
            'image/%s' % size, 'image/large', 'image/small',
            'image/thumbnail'
        ])

    def get_label2(self, default=None):
        return self.get_title()

    def get_label(self, default=None):
        artist = self.get_artist() or 'VA'
        return '%s - %s' % (artist, self.get_title())

    def get_year(self):
        date = self.get_property('released_at', default=None)
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except Exception:
            logger.warn('Invalid date format %s', date)
        return year
