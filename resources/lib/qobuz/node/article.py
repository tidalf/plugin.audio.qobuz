'''
    qobuz.node.article
    ~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from kodi_six import xbmcgui

from qobuz.api import api
from qobuz.debug import getLogger
from qobuz.gui.contextmenu import contextMenu
from qobuz.node import Flag
from qobuz.node import getNode
from qobuz.node.inode import INode

logger = getLogger(__name__)


class WidgetArticle(xbmcgui.WindowDialog):
    def __init__(self, *a, **ka):
        super(WidgetArticle, self).__init__()

    def onInit(self):
        self.image = xbmcgui.ControlImage(100, 250, 125, 75, aspectRatio=2)

    def onClick(self, action):
        super(WidgetArticle, self).onClick(action)

    def onAction(self, action):
        super(WidgetArticle, self).onAction(action)

    def onFocus(self, action):
        super(WidgetArticle, self).onFocus(action)


def dialog(heading='Article', txt=''):
    dialog = xbmcgui.Dialog()
    return dialog.ok(heading, txt)


class Node_article(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_article, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.ARTICLE
        self.content_type = 'artists'

    def get_label(self):
        if self.nid is None:
            return 'Articles (i8n)'
        return '%s (%s)' % (self.get_property('title'),
                            self.get_property('author'))

    def get_label2(self):
        return self.get_property('type')

    def makeListItem(self, **ka):
        item = xbmcgui.ListItem(self.get_label(),
                                self.get_property('source'),
                                self.get_image(), self.get_image())
        item.setInfo(
            'Music',
            infoLabels={
                'artist': self.get_author(),
                'genre': self.get_genre()
            })
        item.setProperty('artist_genre', self.get_genre())
        item.setProperty('artist_description', self.get_description())
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), ka['replaceItems'])
        return item

    def get_author(self):
        return self.get_property('author')

    def get_genre(self):
        return '%s - %s' % (self.get_property('source'),
                            self.get_property('category'))

    def get_description(self, abstract=True):
        if self.nid is None:
            return self.get_property('abstract', to='strip_html')
        return self.get_property('content', to='strip_html')

    def get_title(self):
        return self.get_property('title')

    def get_image(self):
        image = self.get_property('image')
        if image is not None:
            image = image.replace('http://player.', 'http://www.')
        return image

    def fetch(self, *a, **ka):
        if self.nid is None:
            return api.get('/article/listLastArticles',
                           offset=self.offset,
                           limit=self.limit)
        return api.get('/article/get', article_id=self.nid)

    def _populate_articles(self, *a, **ka):
        for item in self.data['articles']['items']:
            self.add_child(
                getNode(
                    Flag.ARTICLE, parameters={'nid': item['id']}, data=item))
        return True if len(self.data['articles']['items']) > 0 else False

    def _populate_one(self, *a, **ka):
        logger.info('ONE: %s', self.data)
        dialog(self.get_title(), self.get_description())
        return True

    def populate(self, *a, **ka):
        if self.nid is None:
            return self._populate_articles(*a, **ka)
        return self._populate_one(*a, **ka)
