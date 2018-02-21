'''
    default
    ~~~~~~~
    :note: Kodi addon entry point
    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
from os import path as P
sys.path.append(P.join(P.abspath(P.dirname(__file__)), 'resources', 'lib'))

from qobuz.plugin import Plugin  # pylint: disable=C0413
from qobuz.application import Application  # pylint: disable=C0413

with Application(Plugin('plugin.audio.qobuz')) as app:
    app.start()
