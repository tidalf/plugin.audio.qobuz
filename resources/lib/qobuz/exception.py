'''
    qobuz.exception
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

class QobuzError(Exception):
    pass

class InvalidParameter(QobuzError):
    pass

class MissingParameter(QobuzError):
    pass

class MissingAgument(QobuzError):
    pass

class InvalidFlag(QobuzError):
    pass

class InvalidKind(QobuzError):
    pass

class BuildCanceled(QobuzError):
    pass

class InvalidNodeType(QobuzError):
    pass

class InvalidLogin(QobuzError):
    pass

class UnknownMode(QobuzError):
    pass

class InvalidSearchType(QobuzError):
    pass

class InvalidDebugPath(QobuzError):
    pass

class DirectoryNotWritable(QobuzError):
    pass
