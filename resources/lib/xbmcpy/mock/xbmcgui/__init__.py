'''
    xbmcpy.mock.xbmcgui
    ~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
class Mock(object):

    def __init__(self):
        self.items = []

    def ListItem(self, label, label2=None, image=None, thumb=None, url=None):
        self.items.append((label, label2, image, thumb, url))
    
    def Dialog(self):
        raise NotImplementedError('Dialog')
    
    def Window(self):
        raise NotImplementedError('Window')
try:
    import xbmcgui # @UnresolvedImport
except:
    xbmcgui = Mock()

