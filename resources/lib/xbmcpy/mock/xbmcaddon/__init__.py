import os
from xbmcpy.mock.xbmc import xbmc
_addon_id_ = None

class __Addon__(object):

    __info_keys = ['author', 'changelog', 'description', 'disclaimer', 
                       'fanart', 'icon', 'id', 'name', 'path', 'profile', 
                       'stars', 'summary', 'type', 'version']
    
    def __init__(self):
        self.xmlroot = None

    def getAddonInfo(self, key):
        if not key in self.__info_keys:
            raise KeyError(key)
        if key == 'id':
            return _addon_id_
        if key == 'path':
            return os.path.abspath(os.path.join(os.path.curdir, '..'))
        if key == 'version':
            return '0.0.1'
        return 'key: NotImplemented'
    
    def __get_xml_root(self):
        import xml.etree.ElementTree as ET
        return ET.parse(os.path.join(xbmc.translatePath('special://profile/'), 
                                     'addon_data', self.getAddonInfo('id'), 
                                     'settings.xml'))
    def getSetting(self, sid):
        if not self.xmlroot:
            self.xmlroot = self.__get_xml_root()
        elm = self.xmlroot.find('.//setting[@id="%s"]' % (sid))
        if elm is not None:
            elm = elm.get('value')
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
