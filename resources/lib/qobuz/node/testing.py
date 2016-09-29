'''
    qobuz.node.collections
    ~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import lang, getImage
from qobuz.node import getNode, Flag
from qobuz import debug
import requests

class Node_testing(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_testing, self).__init__(parent=parent,
                                               parameters=parameters,
                                               data=data)
        self.nt = Flag.TESTING
        self.label = 'Testing'
        self.content_type = 'albums'
        #self.image = getImage('album')
        self.api_url = 'http://127.0.0.1:33574'

    def add_text(self, text='n/a'):
        self.add_child(getNode(Flag.TEXT, {'label': text}))

    def _httpd_running(self):
        def test():
            res = None
            try:
                res = requests.get('%s/qobuz/ping' % self.api_url)
            except requests.ConnectionError as e:
                debug.error(self, 'HTTPD service not running? {}', e)
                return False
            if res is None:
                return False
            debug.info(self, 'code {}', res)
            if res.status_code != 404:
                return False
            return True
        self.add_text('- httpd service: %s' % test())
        self.add_text('            url: %s' % self.api_url)

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        self._httpd_running()
        return True
