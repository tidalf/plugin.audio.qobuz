'''
    qobuz.debug
    ~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

__all__ = ['log_facility', 'log', 'warn']


class Logger(object):

    DEBUG = 'DEBUG'
    NOTICE = 'NOTICE'
    ERROR = 'ERROR'
    SEVERE = 'SEVERE'

    def __obj_name__(self, obj):
        name = None
        if isinstance(obj, basestring):
            name = obj
        else:
            try:
                name = obj.__class__.__name__
            except:
                name = type(obj)
        return name

    def log(self, obj, msg):
        name = self.__obj_name__(obj)
        print '[%s] %s %s' % (self.NOTICE, name, msg)

    def warn(self, obj, msg):
        name = self.__obj_name__(obj)
        print '[%s] %s %s' % (self.ERROR, name, msg)

    def error(self, obj, msg):
        name = self.__obj_name__(obj)
        print '[%s] %s %s' % (self.SEVERE, name, msg)


class LogFacility(object):

    def __init__(self, logger):
        self.logger = logger

    def log(self, obj, msg):
        self.logger.log(obj, msg)

    def warn(self, obj, msg):
        self.logger.warn(obj, msg)

    def error(self, obj, msg):
        self.logger.error(obj, msg)

log_facility = LogFacility(Logger())


def log(obj, msg):
    global log_facility
    log_facility.log(obj, msg)


def warn(obj, msg):
    global log_facility
    log_facility.warn(obj, msg)


def error(obj, msg):
    global log_facility
    log_facility.error(obj, msg)

#
# __debugging__ = True
# ourlog = None
# LOGDEBUG = None
# LOGNOTICE = None
# LOGERROR = None
# LOGSEVERE = None
#
# try:
#    import xbmc
#    import xbmcaddon           # @UnresolvedImport
#    ourlog = xbmc.log          # @UndefinedVariable
#    LOGDEBUG = xbmc.LOGDEBUG   # @UndefinedVariable
#    LOGNOTICE = xbmc.LOGNOTICE # @UndefinedVariable
#    LOGERROR = xbmc.LOGERROR   # @UndefinedVariable
#    LOGSEVERE = xbmc.LOGSEVERE # @UndefinedVariable
#    __debugging__ = False
#    if xbmcaddon.Addon(id='plugin.audio.qobuz').getSetting('debug') == 'true':
#        __debugging__ = True
# except:
#    LOGDEBUG = '[DEBUG]'
#    LOGNOTICE = '[NOTICE]'
#    LOGERROR = '[ERROR]'
#    LOGSEVERE = '[SEVERE]'
#
#    def logfunc(msg, lvl):
#        print lvl + msg
#    ourlog = logfunc
#
# def log(obj, msg, lvl=LOGNOTICE):
#    """Base for all logging function, run in/out Xbmc
#        Inside Xbmc loggin functions use xbmc.log else they just print
#        message to STDOUT
#    """
#    if not __debugging__:
#        return
#    name = None
#    if isinstance(obj, basestring):
#        name = obj
#    else:
#        try:
#            name = obj.__class__.__name__
#        except:
#            name = type(obj)
#    ourlog('[Qobuz/' + str(name) + "] " + msg, lvl)
#
# def warn(obj, msg):
#    """facility: LOGERROR
#    """
#    log(obj, msg, LOGERROR)
#
# def info(obj, msg):
#    """facility: LOGNOTICE
#    """
#    log(obj, msg, LOGNOTICE)
#
# def debug(obj, msg):
#    """facility: LOGDEBUG
#    """
#    log(obj, msg, LOGDEBUG)
#
# def error(obj, msg):
#    """facility: LOGSEVERE
#    """
#    log(obj, msg, LOGSEVERE)
