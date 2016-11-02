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

    def get_label(self):
        return self.message()

    def add_text(self, text='n/a'):
        self.add_child(getNode(Flag.TEXT, parameters={'label': text}))

    def fetch(self, *a, **ka):
        res = None
        try:
            res = requests.get('%s/qobuz/ping' % self.api_url)
        except requests.ConnectionError as e:
            debug.error(self, 'HTTPD service not running? {}', e)
        return res

    def message(self):
        out = ''
        if config.app.registry.get('enable_scan_feature', to='bool'):
            out += '''- endPoint: {url}
- running: {is_alive}
Tip: You can disable/enable Qobuz addon to restart web service
        '''.format(url=self.api_url, is_alive=self.is_alive())
        return out

    def is_alive(self):
        self.data = self.fetch()
        if self.data is None:
            return False
        if self.data.status_code != 200:
            return False
        return True

    def show_dialog(self):
        d = xbmcgui.Dialog()
        d.ok('Web service', self.message())

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        self.add_child(getNode(Flag.TEXT,
                               parameters={'label': self.message()}))
        return True
