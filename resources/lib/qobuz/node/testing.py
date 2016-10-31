'''
    qobuz.node.collections
    ~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz import config
from qobuz.node import getNode, Flag
from qobuz import debug
import requests

import xbmcgui
class Window(xbmcgui.Window):
    pass

class Node_testing(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_testing, self).__init__(parent=parent,
                                               parameters=parameters,
                                               data=data)
        self.nt = Flag.TESTING
        self.label = 'Testing'
        self.content_type = 'files'
        self.api_url = 'http://{host}:{port}'.format(
            host=config.app.registry.get('httpd_host'),
            port=config.app.registry.get('httpd_port'))

    def add_text(self, text='n/a'):
        self.add_child(getNode(Flag.TEXT, {'label': text}))

    def window_httpd(self):
        def test():
            res = None
            try:
                res = requests.get('%s/qobuz/ping' % self.api_url)
            except requests.ConnectionError as e:
                debug.error(self, 'HTTPD service not running? {}', e)
                return False
            if res is None:
                return False
            if res.status_code != 200:
                return False
            return True
        d = xbmcgui.Dialog()
        d.ok('Web service / Kooli',
             'Testing web service: %s' % self.api_url,
             '- running: %s' % test(),
             'Tip: You can disable/enable Qobuz addon to restart web service')
    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        #self._httpd_running()
        return True
