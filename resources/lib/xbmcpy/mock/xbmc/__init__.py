'''
    xbmcpy.mock.xbmc
    ~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
__all__ = ['xbmc']
try:
    import xbmc
except:
    from _xbmc import mock as xbmc