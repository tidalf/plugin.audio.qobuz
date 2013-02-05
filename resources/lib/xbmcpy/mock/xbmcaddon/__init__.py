'''
    xbmcpy.mock.xbmcaddon
    ~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
from xbmcpy.mock.xbmc import xbmc
_addon_id_ = None

class __Addon__(object):

    __info_keys = ['author', 'changelog', 'description', 'disclaimer', 
                       'fanart', 'icon', 'id', 'name', 'path', 'profile', 
                       'stars', 'summary', 'type', 'version']

    def __init__(self):
        self.xmlroot_config = None
        self.xmlroot_language = None

    def getAddonInfo(self, key):
        if not key in self.__info_keys:
            raise KeyError(key)
        if key == 'id':
            return _addon_id_
        if key == 'path':
            return os.path.abspath(os.path.join(os.path.curdir, '..'))
        if key == 'version':
            return '0.0.1'
        return 'key %s: NotImplemented' % (key)

    def __get_config_xml_root(self):
        import xml.etree.ElementTree as ET
        return ET.parse(os.path.join(xbmc.translatePath('special://profile/'), 
                                     'addon_data', self.getAddonInfo('id'), 
                                     'settings.xml'))

    def __get_language_xml_root(self):
        import xml.etree.ElementTree as ET
        return ET.parse(os.path.join(self.getAddonInfo('path'), 'language', 
                                     'English', 'strings.xml'))

    def getSetting(self, sid):
        if not self.xmlroot_config:
            self.xmlroot_config = self.__get_config_xml_root()
        #@bug: error on linux (debian/squeeze) with python 2.6
        elm = self.xmlroot_config.find('.//setting[@id="%s"]' % (sid)) 
        if elm is not None:
            elm = elm.get('value')
        return elm

    def getLocalizedString(self, sid):
        if not self.xmlroot_language:
            self.xmlroot_language = self.__get_language_xml_root()
        elm = self.xmlroot_language.find('.//string[@id="%s"]' % (sid))
        if elm is not None:
            elm = elm.text
        return elm

Addon = None
try:
    import xbmcaddon
    Addon = xbmcaddon.Addon
except:
    Addon = __Addon__
    class _xbmc_(): pass
    xbmcaddon = _xbmc_()
    xbmcaddon.Addon = Addon
