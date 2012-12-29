#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.

import xbmc, xbmcgui,xbmcplugin
import qobuz

'''
    Keyboard
'''
class Keyboard(xbmc.Keyboard):
    
    def __init__(self, default, heading, hidden = True):
        self.setHeading('Qobuz / ' + heading)
        

def getImage(name):
    path = qobuz.path.image + '/' + name + '.png'
    return path

'''
    Notify Human
'''
def notifyH(title, text, image = None, mstime = 2000):
    image = image or getImage('default')
    s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (title, text, mstime, image)
    xbmc.executebuiltin(s.encode('utf-8', 'replace'))

'''
    Notify
'''
def notify(title, text, image = None, mstime = 2000):
    image = image or getImage('default')
    s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (lang(title), lang(text), mstime, getImage)
    xbmc.executebuiltin(s.encode('utf-8', 'replace'))
    
def dialogLoginFailure():
    import sys
    dialog = xbmcgui.Dialog()
    if dialog.yesno(lang(30008), lang(30034), lang(30040)):
        qobuz.addon.openSettings()
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]), succeeded = False, updateListing = True, cacheToDisc = False)    
    else:
        xbmc.executebuiltin('ActivateWindow(home)')
        return False

def isFreeAccount():
    data = qobuz.registry.get(name='user')
    if not data: return True
    if not data['data']['user']['credential']['id']: 
        return True
    return False

def dialogFreeAccount():
    if qobuz.addon.getSetting('warn_free_account') != 'true':
        return
    dialog = xbmcgui.Dialog()
    ok = dialog.yesno(lang(41000), lang(41001), lang(41002), lang(41003))
    if ok:
        qobuz.addon.setSetting('warn_free_account', 'false')

def executeJSONRPC(json):
    return xbmc.executeJSONRPC(json)

def color(colorItem, msg):
    return '[COLOR=' + colorItem + ']' + msg + '[/COLOR]'

def lang(langId):
    return qobuz.addon.getLocalizedString(langId)


