'''
    qobuz.gui.utils
    ~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys

from qobuz import config
from qobuz.debug import getLogger
from qobuz.xbmcrpc import showNotification, getInfoLabels
import qobuz

logger = getLogger(__name__)

try:
    from kodi_six import xbmc, xbmcgui, xbmcplugin  # pylint:disable=E0401

    class Keyboard(xbmc.Keyboard):
        def __init__(self, _default, heading='', _hidden=True):
            self.setHeading('Qobuz / %s' % heading)

except Exception as e:
    logger.warn('QobuzXBMC WARNING: Used outside of xbmc, '
                'lot of thing broken %s', e)


def ask(current=None, heading='rename'):
    w = Keyboard(current, heading)
    w.doModal()
    if not w.isConfirmed():
        return None
    return w.getText().strip()


def getImage(name):
    if name is None:
        return ''
    if name.startswith('http'):
        return name
    if not config.path:
        return ''
    return os.path.join(config.path.image, name + '.png')


def notifyH(title, text, image=None, mstime=2000):
    '''Notify for human... not using localized string :p
    '''
    if image is None:
        image = getImage('icon-default-256')
    else:
        image = getImage(image)
    return showNotification(
        title=title, message=text, image=image, displaytime=mstime)


def notify_log(title, text, **ka):
    return notifyH(title, text, image='icon-default-256', **ka)


def notify_error(title, text, **ka):
    return notifyH(title, text, image='icon-error-256', **ka)


def notify_warn(title, text, **ka):
    return notifyH(title, text, image='icon-warn-256', **ka)


def notify(title, text, image=None, mstime=2000):
    '''Notification that wrap title and text parameter into lang()
    '''
    if image is None:
        image = getImage('icon-default-256')
    else:
        image = getImage(image)
    return showNotification(
        title=lang(title), message=lang(text), image=image, displaytime=mstime)


def dialogLoginFailure():
    '''Dialog to be shown when we can't login into Qobuz
    '''
    dialog = xbmcgui.Dialog()
    if dialog.yesno(lang(30010), lang(30036), lang(30042)):
        qobuz.addon.openSettings()
        xbmcplugin.endOfDirectory(
            handle=int(sys.argv[1]),
            succeeded=False,
            updateListing=True,
            cacheToDisc=False)
    else:
        xbmc.executebuiltin('ActivateWindow(home)')
        return False


def dialogServiceTemporarilyUnavailable():
    '''Dialog to be shown when Qobuz is not available (Maintenance)
    '''
    dialog = xbmcgui.Dialog()
    dialog.ok('Qobuz Service Temporay Unavailable',
              'Qobuz service are down :/', 'Check it later')
    xbmcplugin.endOfDirectory(
        handle=int(sys.argv[1]),
        succeeded=False,
        updateListing=True,
        cacheToDisc=False)
    return False


def isFreeAccount():
    '''Check if account if it's a Qobuz paid account
    '''
    from qobuz.api.user import current
    return current.is_free_account()


def dialogFreeAccount():
    '''Show dialog when using free acccount
    '''
    if qobuz.addon.getSetting('warn_free_account') != 'true':
        return
    dialog = xbmcgui.Dialog()
    ok = dialog.yesno(lang(30175), lang(30176), lang(30177), lang(30178))
    if ok:
        qobuz.addon.setSetting('warn_free_account', 'false')


def executeJSONRPC(json):
    return xbmc.executeJSONRPC(json)


def lang(langId):
    s = config.app.addon.getLocalizedString(langId)
    if not s:
        raise KeyError(langId)
    return s


def runPlugin(url):
    return 'XBMC.RunPlugin("%s")' % url


def containerUpdate(url, replace=False):
    replace_string = ''
    if replace is True:
        replace_string = ', "replace"'
    return 'Container.Update("%s"%s)' % (url, replace_string)


def yesno(heading, line1, line2='', line3=''):
    dialog = xbmcgui.Dialog()
    return dialog.yesno(heading, line1, line2, line3)


def containerRefresh():
    return 'Container.Refresh'


def executeBuiltin(cmd):
    xbmc.executebuiltin(cmd)


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
