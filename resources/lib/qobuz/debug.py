'''
    qobuz.debug
    ~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
from os import path as P
import logging

FORMAT = "%(levelname)s:%(name)s: %(message)s"
FORMAT_KODI = "[%(name)s] %(message)s"
FORMATER = logging.Formatter(FORMAT)
LOGPATH = P.expanduser(P.join('~', 'plugin.audio.qobuz.log'))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def attach_file_logger(logger):
    handler = logging.FileHandler(LOGPATH)
    logger.addHandler(handler)


try:
    import xbmc
    import xbmcaddon

    class XbmcLogger(logging.Handler):

        def __init__(self, *a, **ka):
            super(XbmcLogger, self).__init__(*a, **ka)
            self.fmt = logging.Formatter(FORMAT_KODI)

        def handle(self, record):
            if record.levelname == 'WARNING':
                xbmc.log(self.fmt.format(record), xbmc.LOGWARNING)
            if record.levelname == 'DEBUG':
                xbmc.log(self.fmt.format(record), xbmc.LOGDEBUG)
            if record.levelname == 'INFO':
                xbmc.log(self.fmt.format(record), xbmc.LOGNOTICE)
            elif record.levelname == 'ERROR':
                xbmc.log(self.fmt.format(record), xbmc.LOGERROR)
            elif record.levelname == 'CRITICAL':
                xbmc.log(self.fmt.format(record), xbmc.LOGSEVERE)
            else:
                xbmc.log(self.fmt.format(record), xbmc.LOGNOTICE)

    if xbmcaddon.Addon(id='plugin.audio.qobuz').getSetting('debug') == 'true':
        logger.addHandler(XbmcLogger())

except Exception as e:
    print('Exception %s' % e)  # pylint: disable=E1601
    attach_file_logger(logger)


def get_logger_factory(logger):
    def getLogger(name='main'):
        mylogger = logger.getChild(name)
        return mylogger
    return getLogger


getLogger = get_logger_factory(logger)
