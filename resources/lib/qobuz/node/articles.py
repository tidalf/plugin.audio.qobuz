'''
    qobuz.node.articles
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import xbmcgui
import xbmc

import qobuz
from flag import NodeFlag as Flag
from inode import INode
from article import Node_article
from gui.util import getImage, getSetting

'''
    @class Node_articles
'''

class Node_articles(INode):

    def __init__(self, parent=None, parameters=None):
        super(Node_articles, self).__init__(parent, parameters)
        self.type = Flag.ARTICLES
        self.is_folder = True
        self.image = getImage('album')
        self.offset = self.get_parameter('offset') or 0

    
    def get_label(self):
        l = self.get_property('title')
        if not l: return "Articles"
        return l

    def fetch(self, Dir, lvl , whiteFlag, blackFlag):
        limit = getSetting('pagination_limit')
        data = qobuz.registry.get(name='article_listlastarticles',
                                      id=self.id, 
                                      rubric_ids=self.id,
                                      offset=self.offset, 
                                      limit=limit)
        if not data: 
            return False
        self.data = data['data']
        return True

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        for article in self.data['articles']['items']:
            node = Node_article(self, {'nid': article['id']})
            node.data = article
            self.add_child(node)
