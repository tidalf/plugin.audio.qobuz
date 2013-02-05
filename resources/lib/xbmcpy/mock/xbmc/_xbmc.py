'''
    xbmcpy.mock.xbmc._xbmc
    ~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os, getpass, sys, platform

'''Our platform
'''
_platform_ = platform.platform(False, True).lower()

''' Fake special://profile/
'''
_fake_profile = None

if _platform_.startswith('windows-7'):
    _fake_profile = os.path.join('c:\\', 'Users', getpass.getuser(), 
                                 'AppData', 'Roaming', 'XBMC', 'userdata')
elif _platform_.startswith('linux'):
    _fake_profile = os.path.join('/', 'home', getpass.getuser(), '.xbmc', 'userdata')
else:
    raise NotImplementedError('fake_profile for os: %s' % (_platform_))

class _Player_():
    pass
    
class Mock(object):
    ''' <xbmc> mock
    '''
    def __init__(self):
        self.Player = _Player_

    def translatePath(self, path):
        if path.startswith('special://profile'):
            return _fake_profile
        return path

'''singleton
'''
mock = Mock()
