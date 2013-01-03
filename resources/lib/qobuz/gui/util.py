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
import os, sys
import xbmc
import xbmcgui
import xbmcplugin
from debug import log, debug
import qobuz

from xbmcrpc import showNotification, getInfoLabels

'''
    Keyboard
'''

class Keyboard(xbmc.Keyboard):

    def __init__(self, default, heading, hidden=True):
        self.setHeading('Qobuz / ' + heading)


def getImage(name):
    return os.path.join(qobuz.path.image, name + '.png')

'''
    Notify Human
'''
def notifyH(title, text, image=None, mstime=2000):
    if not image:
        image = getImage('icon-default-256')
    print "CurrentViewMode: %s" % (containerViewMode())
    print "CurrentViewMode: %s" % (containerSortMethod())
    return showNotification(title=title, message=text, image=image, displaytime=mstime)

'''
    Notify
'''
def notify(title, text, image=None, mstime=2000):
    if not image:
        image = getImage('icon-default-256')
    return showNotification(title=lang(title), 
                     message=lang(text), 
                     image= getImage, 
                     displaytime=mstime)

def dialogLoginFailure():
    dialog = xbmcgui.Dialog()
    if dialog.yesno(lang(30008), lang(30034), lang(30040)):
        qobuz.addon.openSettings()
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False,
                                  updateListing=True, cacheToDisc=False)
    else:
        xbmc.executebuiltin('ActivateWindow(home)')
        return False


def isFreeAccount():
    data = qobuz.registry.get(name='user')
    if not data:
        return True
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
    if not msg: return ''
    return '[COLOR=%s]%s[/COLOR]' % (colorItem, msg)


def lang(langId):
    return qobuz.addon.getLocalizedString(langId)


def runPlugin(url):
    return 'XBMC.RunPlugin("%s")' % (url)

def containerUpdate(url):
    return ('Container.Update("%s")') % ( url)

def yesno(heading, line1, line2='', line3=''):
    dialog = xbmcgui.Dialog()
    return dialog.yesno(heading, line1, line2, line3)

def containerRefresh():
    xbmc.executebuiltin('Container.Refresh')

def formatControlLabel(label, sFormat=None, colorItem=None):
    if not colorItem: 
        colorItem = qobuz.addon.getSetting('item_section_color')
    if not sFormat:
        sFormat = qobuz.addon.getSetting('item_section_format')
    return sFormat % (color(colorItem, label))

def containerViewMode():
    label = 'Container.Viewmode'
    data = getInfoLabels(labels=[label])
    if data: 
        return data[label]
    return ''

def containerSortMethod():
    label = 'Container.SortMethod'
    data = getInfoLabels(labels=[label])
    print "ID" + repr(getInfoLabels(labels=['ListItem.Property(Node.ID)']))
    print "ID" + repr(getInfoLabels(labels=['ListItem.Property(Node.Type)']))
    if data: 
        return data[label]
    return ''

def setResolvedUrl(**ka):
    return xbmcplugin.setResolvedUrl(**ka)
