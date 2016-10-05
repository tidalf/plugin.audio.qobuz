'''
    qobuz.node.article_rubrics
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import qobuz  # @UnresolvedImport
from qobuz.node.flag import Flag
from qobuz.node.inode import INode
from qobuz.node.articles import Node_articles
from qobuz.gui.util import getImage, getSetting


class Node_article_rubrics(INode):
    '''@class Node_article_rubrics
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_article_rubrics, self).__init__(parent=parent,
                                                   parameters=parameters,
                                                   data=data)
        self.nt = Flag.ARTICLE_RUBRICS
        self.rubric_id = self.get_parameter('qid')
        self.is_folder = True
        self.image = getImage('album')
        self.offset = self.get_parameter('offset') or 0

    def make_url(self, **ka):
        url = super(Node_article_rubrics, self).make_url(**ka)
        if self.rubric_id:
            url += '&qid=' + str(self.rubric_id)
        return url

    def get_label(self):
        l = self.get_property('title')
        if not l:
            return 'Articles'
        return l

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        limit = getSetting('pagination_limit')
        data = qobuz.registry.get(
            name='article_listrubrics',
            id=self.nid, offset=self.offset,
            limit=limit)
        if data is None or not 'data' in data:
            return None
        return data['data']

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for rubric in self.data['rubrics']['items']:
            node = Node_articles(self, {'nid': rubric['id']})
            node.data = rubric
            self.add_child(node)
        return True
