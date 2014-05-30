'''
    xbmcpy.mock.plugin
    ~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012-2014 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
try:
    import xbmcplugin  # @UnresolvedImport
except:
    from _plugin import plugin as xbmcplugin  # @Reimport
