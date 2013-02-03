import os, getpass, sys, platform
#from xbmcpy.mock import xbmcaddon

'''Our platform
'''
_platform_ = platform.platform(False, True).lower()

''' Fake special://profile/
'''
_fake_profile = None

if _platform_.startswith('windows-7'):
    _fake_profile = os.path.join('c:\\', 'Users', getpass.getuser(), 
                                 'AppData', 'Roaming', 'XBMC', 'userdata')
else:
    raise NotImplementedError('fake_profile for os: %s' % (_platform_))

'''xbmc mock
'''
class Mock(object):

    def translatePath(self, path):
        if path.startswith('special://profile'):
            return _fake_profile
        return path

'''singleton
'''
xbmc = Mock()