'''
    qobuz.debug
    ~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
from os import path as P
from qobuz import exception as exc

__debugging__ = True
ourlog = None
LOGDEBUG = None
LOGNOTICE = None
LOGERROR = None
LOGSEVERE = None
LOGWARNING = None
filename = None  #'~/qobuz.log'

if filename is not None:
    filename = P.abspath(P.expanduser(filename))
    base = P.dirname(filename)
    if not P.exists(base):
        raise exc.InvalidDebugPath(filename)
    if not os.access(base, os.W_OK):
        raise exc.DirectoryNotWritable(filename)
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


def clear(msg='--- kodi/plugin/qobuz ---\n'):
    if filename is not None:
        with open(filename, 'a+') as fh:
            fh.write(msg)


def _log(obj, lvl, *a, **ka):
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
    msg = '[Qobuz/{name}][{level}] {msg}'.format(
        name=str(name), msg=msg, level=lvl)
    if filename is not None:
        with open(filename, 'a+') as fh:
            fh.write('%s\n' % msg)
    ourlog(msg, lvl)


def warn(obj, *a, **ka):
    _log(obj, LOGWARNING, *a, **ka)


def info(obj, *a, **ka):
    _log(obj, LOGNOTICE, *a, **ka)


def debug(obj, *a, **ka):
    _log(obj, LOGDEBUG, *a, **ka)


def error(obj, *a, **ka):
    _log(obj, LOGERROR, *a, **ka)
