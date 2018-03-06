'''
    qobuz.node.article_rubrics
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.gui.util import getImage
from qobuz.node.article import Node_article
from qobuz.node.flag import Flag
from qobuz.node.inode import INode
import qobuz


class Node_article_rubrics(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_article_rubrics, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.ARTICLE_RUBRICS
        self.rubric_id = self.get_parameter('qid')
        self.image = getImage('album')

    def make_url(self, **ka):
        url = super(Node_article_rubrics, self).make_url(**ka)
        if self.rubric_id:
            url += '&qid={}'.format(self.rubric_id)
        return url

    def get_label(self, default=None):
        title = self.get_property('title')
        if not title:
            return 'Articles'
        return title

    def fetch(self, options=None):
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(name='article_listrubrics',
                                  id=self.nid,
                                  offset=self.offset,
                                  limit=limit)
        if data is None or 'data' not in data:
            return None
        return data['data']

    def populate(self, options=None):
        for rubric in self.data['rubrics']['items']:
            self.add_child(
                Node_article(
                    self, {'nid': rubric['id']}, data=rubric))
        return True
