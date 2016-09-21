'''
    qobuz.debug
    ~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
__debugging__ = True
ourlog = None
LOGDEBUG = None
LOGNOTICE = None
LOGERROR = None
LOGSEVERE = None
LOGWARNING = None

try:
    import xbmc  # @UnresolvedImport
    import xbmcaddon  # @UnresolvedImport
    ourlog = xbmc.log
    LOGDEBUG = xbmc.LOGDEBUG
    LOGNOTICE = xbmc.LOGNOTICE
    LOGERROR = xbmc.LOGERROR
    LOGSEVERE = xbmc.LOGSEVERE
    LOGWARNING = xbmc.LOGWARNING
    __debugging__ = False
    if xbmcaddon.Addon(id='plugin.audio.qobuz').getSetting('debug') == 'true':
        __debugging__ = True
except Exception as e:
    print('Not inside Kodi, Error %s' % e)
    LOGDEBUG = '[DEBUG]'
    LOGNOTICE = '[NOTICE]'
    LOGERROR = '[ERROR]'
    LOGSEVERE = '[SEVERE]'
    LOGWARNING = '[WARNING]'

    def logfunc(msg, lvl):
        print('[%s] %s' % (lvl, msg))
    ourlog = logfunc


def log(obj, lvl, *a, **ka):
    '''Base for all logging function, run in/out Xbmc
        Inside Xbmc loggin functions use xbmc.log else they just print
        message to STDOUT
    '''
    if not __debugging__:
        return
    name = None
    if isinstance(obj, basestring):
        name = obj
    else:
        try:
            name = obj.__class__.__name__
        except:
            name = type(obj)
    msg = None
    num_argument = len(a)
    if num_argument == 1:
        msg = a[0].format(lvl=lvl, **ka)
    elif num_argument > 1:
        msg = a[0].format(lvl=lvl, *a[1:], **ka)
    ourlog('[Qobuz/{name}][{level}] {msg}'
            .format(name=str(name), msg=msg, level=lvl), lvl)

def warn(obj, *a, **ka):
    log(obj, LOGWARNING, *a, **ka)

def info(obj, *a, **ka):
    log(obj, LOGNOTICE, *a, **ka)

def debug(obj, *a, **ka):
    log(obj, LOGDEBUG, *a, **ka)

def error(obj, *a, **ka):
    log(obj, LOGERROR, *a, **ka)
