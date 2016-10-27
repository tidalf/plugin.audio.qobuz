'''
    qobuz.node.search_result
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz import debug
from qobuz.node.inode import INode
from qobuz import exception
from qobuz.gui.util import lang, getImage, getSetting
from qobuz.api import api
from qobuz.node import getNode, Flag


class Node_search_result(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_search_result, self).__init__(parent=parent,
                                          parameters=parameters,
                                          data=data)
        self.nt = Flag.SEARCH_RESULT
        self.label = 'Result {}'.format(self.get_parameter('query', to='unquote'))

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        query = self.get_parameter('query', to='unquote')
        return api.get('/search/getResults',
                       query=query,
                       type=self.get_parameter('search-type'),
                       limit=self.limit,
                       offset=self.offset)

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        search_type = self.get_parameter('search-type')
        flag = None
        if search_type == 'albums':
            flag = Flag.ALBUM
        elif search_type == 'artists':
            flag = Flag.ARTIST
        elif search_type == 'tracks':
            flag = Flag.TRACK
        if len(self.data[search_type]['items']) <= 0:
            return False
        for data in self.data[search_type]['items']:
            self.add_child(getNode(flag, data=data))
        return True
