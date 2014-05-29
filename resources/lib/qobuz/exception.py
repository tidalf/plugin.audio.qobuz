'''
    qobuz.exception
    ~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''


class QobuzException(Exception):
    pass


class InvalidParameter(QobuzException):
    pass


class MissingParameter(QobuzException):
    pass


class InvalidType(QobuzException):
    pass
