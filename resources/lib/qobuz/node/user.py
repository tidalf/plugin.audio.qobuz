'''
    qobuz.node.user
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import getImage, color
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.api.user import current as user
from qobuz import config

class Node_user(INode):
    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_user, self).__init__(parent=parent,
                                         parameters=parameters,
                                         data=data)
        self.nt = Flag.USER
        self.content_type = 'artists'
        self.is_folder = False

    def get_label(self, fmt=''):
        return u'[{login} - {subscription}]'.format(
            login=user.get_property('user/login', default='Demo'),
            country=user.get_property('user/country_code'),
            lang=user.get_property('user/language_code'),
            subscription=user.get_property('user/credential/label', default='Free')
        )

    def get_image(self):
        return user.get_property('user/avatar')

    def fetch(self, *a, **ka):
        return user.data

    def makeListItem(self, replaceItems=False):
        import xbmcgui  # @UnresolvedImport
        item = xbmcgui.ListItem(self.get_label(),
                                self.get_label2(),
                                self.get_image(),
                                self.get_image(),
                                None)
        if not item:
            debug.warn(self, 'Error: Cannot make xbmc list item')
            return None
        #item.setPath(self.make_url())
        item.setInfo('Music', infoLabels={
            'Artist': user.get_property('user/login'),
            'description': user.get_property('user/credential/description')
        })
        #ctxMenu = contextMenu()
        #self.attach_context_menu(item, ctxMenu)
        #item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item
