'''
    qobuz.node.testing
    ~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz import config
from qobuz.debug import getLogger
from qobuz.node import getNode, Flag
from qobuz.node.inode import INode
from time import time
import requests
from kodi_six import xbmcgui

logger = getLogger(__name__)


class Window(xbmcgui.Window):
    pass


class Node_testing(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_testing, self).__init__(
            parent=parent, parameters=parameters, data=data)
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
        start = time()
        try:
            res = requests.get('%s/qobuz/ping' % self.api_url)
        except Exception as e:
            logger.error('Ping httpd fail: %s', e)
            return None
        if res is None or res.status_code != 200:
            return None
        return {'ping:': time() - start}

    def message(self):
        out = ''
        if config.app.registry.get('enable_scan_feature', to='bool'):
            out += '''- endPoint: {url}
- running: {is_alive}
Tip: You can disable/enable Qobuz addon to restart web service
        '''.format(
                url=self.api_url, is_alive=self.is_alive())
        return out

    def is_alive(self):
        if self.fetch() is None:
            return False
        return True

    def show_dialog(self):
        d = xbmcgui.Dialog()
        d.ok('Web service', self.message())

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        self.add_child(
            getNode(
                Flag.TEXT, parameters={'label': self.message()}))
        return True
