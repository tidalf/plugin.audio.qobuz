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

try:
    import xbmc  # @UnresolvedImport
    import xbmcaddon  # @UnresolvedImport
    ourlog = xbmc.log
    LOGDEBUG = xbmc.LOGDEBUG
    LOGNOTICE = xbmc.LOGNOTICE
    LOGERROR = xbmc.LOGERROR
    LOGSEVERE = xbmc.LOGSEVERE
    __debugging__ = False
    if xbmcaddon.Addon(id='plugin.audio.qobuz').getSetting('debug') == 'true':
        __debugging__ = True
except Exception as e:
    print('Not inside Kodi, Error %s', e)
    LOGDEBUG = '[DEBUG]'
    LOGNOTICE = '[NOTICE]'
    LOGERROR = '[ERROR]'
    LOGSEVERE = '[SEVERE]'

    def logfunc(msg, lvl):
        print('[%s] %s' % (lvl, msg))
    ourlog = logfunc


def log(obj, *a, **ka):
    '''Base for all logging function, run in/out Xbmc
        Inside Xbmc loggin functions use xbmc.log else they just print
        message to STDOUT
    '''
    lvl = LOGNOTICE
    if 'lvl' in ka:
        lvl = ka['lvl']
        del ka['lvl']
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
        msg = a[0].format(**ka)
    elif num_argument > 1:
        msg = a[0].format(*a[1:], **ka)
    ourlog('[Qobuz/{name}][{level}] {msg}'
            .format(name=str(name), msg=msg, level=lvl), lvl)


def warn(obj, *a, **ka):
    '''facility: LOGERROR'''
    ka['lvl']= LOGERROR
    log(obj, *a, **ka)


def info(obj, *a, **ka):
    '''facility: LOGNOTICE'''
    ka['lvl'] = LOGNOTICE
    log(obj, *a, **ka)


def debug(obj, *a, **ka):
    '''facility: LOGDEBUG'''
    ka['lvl'] = LOGDEBUG
    log(obj, *a, **ka)


def error(obj, *a, **ka):
    '''facility: LOGSEVERE'''
    log(obj, *a, **ka)
