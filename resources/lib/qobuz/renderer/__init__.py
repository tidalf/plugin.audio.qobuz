'''
    qobuz.renderer
    ~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.renderer.xbmc import QobuzXbmcRenderer as OurRenderer
from qobuz.node import Flag

def renderer(nType, params=None, mode=None, whiteFlag=Flag.ALL,
             blackFlag=Flag.STOPBUILD):
    return OurRenderer(nType, params, mode, whiteFlag=whiteFlag,
                       blackFlag=blackFlag)
