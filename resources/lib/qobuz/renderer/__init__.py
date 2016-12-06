'''
    qobuz.renderer
    ~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.renderer.xbmc import QobuzXbmcRenderer as OurRenderer
from qobuz.node import Flag
from qobuz.constants import Mode

def renderer(nType,
             parameters={},
             mode=Mode.VIEW,
             whiteFlag=Flag.ALL,
             blackFlag=Flag.STOPBUILD,
             depth=1, asList=False):
    return OurRenderer(nType, parameters=parameters, mode=mode,
                       whiteFlag=whiteFlag, blackFlag=blackFlag,
                       depth=depth, asList=asList)
