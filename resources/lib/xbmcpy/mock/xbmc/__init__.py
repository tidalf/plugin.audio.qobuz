'''
    xbmcpy.mock.xbmc
    ~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012-2014 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
try:
    import xbmc  # @UnresolvedImport
except:
    from _xbmc import mock as xbmc  # @Reimport
