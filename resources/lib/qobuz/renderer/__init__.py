'''
    qobuz.renderer
    ~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.constants import Mode
from qobuz.node import Flag
from qobuz.renderer.xbmc import QobuzXbmcRenderer as OurRenderer


def renderer(nType,
             parameters=None,
             mode=Mode.VIEW,
             whiteFlag=Flag.ALL,
             blackFlag=Flag.STOPBUILD,
             depth=1,
             asList=False):
    parameters = {} if parameters is None else parameters
    return OurRenderer(
        nType,
        parameters=parameters,
        mode=mode,
        whiteFlag=whiteFlag,
        blackFlag=blackFlag,
        depth=depth,
        asList=asList)
