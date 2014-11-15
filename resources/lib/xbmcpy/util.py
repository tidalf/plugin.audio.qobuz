'''
    xbmcpy.util
    ~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012-2014 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys
import re
import mock.xbmcaddon as xbmcaddon
from mock.xbmc import xbmc
import mock.xbmcgui as xbmcgui
from mock.xbmcplugin import xbmcplugin
from rpc import showNotification
import qobuz


def htm2xbmc(htm):
    def replace(m):
        return '[' + m.group(1) + m.group(2).upper() + ']'
    return re.sub('<(/?)(i|b)>', replace, htm, re.IGNORECASE)


def getImage(name):
    return ''
    if not qobuz.path:
        return ''
    return os.path.join(qobuz.path.image, name + '.png')


def notifyH(title, text, image=None, mstime=2000):
    """Notify for human... not using localized string :p
    """
    if not image:
        image = getImage('icon-default-256')
    return showNotification(title=title, message=text, image=image, displaytime=mstime)


def notify(title, text, image=None, mstime=2000):
    """Notification that wrap title and text parameter into lang()
    """
    if not image:
        image = getImage('icon-default-256')
    return showNotification(title=lang(title),
                     message=lang(text),
                     image=getImage,
                     displaytime=mstime)


def dialogLoginFailure():
    """Dialog to be shown when we can't login into Qobuz
    """
    dialog = xbmcgui.Dialog()
    if dialog.yesno(lang(30008), lang(30034), lang(30040)):
        qobuz.addon.openSettings()
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False,
                                  updateListing=True, cacheToDisc=False)
    else:
        xbmc.executebuiltin('ActivateWindow(home)')
        return False


def isFreeAccount():
    """Check if account if it's a Qobuz paid account
    """
    from pyobuz.api import api
    data = api.get('/user/login', username=api.username,
                   password=api.password)
    if not data:
        return True
    if not data['user']['credential']['id']:
        return True
    return False


def dialogFreeAccount():
    """Show dialog when using free acccount
    """
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
    if not colorItem: return msg
    return '[COLOR=%s]%s[/COLOR]' % (colorItem, msg)


def nolang(msg):
    print "[Warn] untranslated string %s" % msg
    return msg


def lang(langId):
    s = xbmcaddon.Addon().getLocalizedString(langId)
    if not s:
        raise KeyError(langId)
    return s


def runPlugin(url):
    return 'XBMC.RunPlugin("%s")' % (url)


def executeBuiltin(cmd):
    xbmc.executebuiltin("%s" % (cmd))  # @UndefinedVariable


def containerUpdate(url, replace=False):
    if replace:
        replace = ', "replace"'
    else:
        replace = ''
    s = 'Container.Update("%s"%s)' % (url, replace)
    return s


def yesno(heading, line1, line2='', line3=''):
    dialog = xbmcgui.Dialog()
    return dialog.yesno(heading, line1, line2, line3)


def containerRefresh():
    return ('Container.Refresh')


def containerViewMode():
    label = 'Container.Viewmode'
    data = getInfoLabels(labels=[label])
    if data:
        return data[label]
    return ''


def containerSortMethod():
    label = 'Container.SortMethod'
    data = getInfoLabels(labels=[label])
    if data:
        return data[label]
    return ''


def setResolvedUrl(**ka):
    return xbmcplugin.setResolvedUrl(**ka)


def getSetting(key, **ka):
    """Helper to access xbmcaddon.getSetting
        Parameter:
        key: Key to retrieve from setting
        * optional: isBool (convert 'true' and 'false to python boolean),
            isInt (return data as integer)
    """
    return ''
    data = qobuz.addon.getSetting(key)
    if not data:
        return ''
    if 'isBool' in ka and ka['isBool']:
        if data == 'true':
            return True
        return False
    if 'isInt' in ka and ka['isInt']:
        return int(data)
    return data
