'''
    qobuz.node.articles
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import xbmcgui
import xbmc

from inode import INode
from node import getNode, Flag

class Node_articles(INode):
    '''
    @class Node_articles
    '''
    def __init__(self, parameters={}):
        super(Node_articles, self).__init__(parent, parameters)
        self.kind = Flag.ARTICLES

    def get_label(self):
        l = self.get_property('title')
        if not l: return "Articles"
        return l

    def fetch(self, renderer=None):
        data = qobuz.registry.get(name='article_listlastarticles',
                                      id=self.nid, 
                                      rubric_ids=self.nid,
                                      offset=self.offset, 
                                      limit=limit)
        if not data: 
            return False
        self.data = data['data']
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for article in self.data['articles']['items']:
            node = getNode(Flag.ARTICLE, {'nid': article['id']})
            node.data = article
            self.add_child(node)
