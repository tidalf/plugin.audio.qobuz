'''
    default
    ~~~~~~~
    :note: Kodi addon entry point
    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import os
sys.path.append(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'resources', 'lib'))

from qobuz.plugin import Plugin
from qobuz.application import Application
from qobuz import debug

with Application(Plugin('plugin.audio.qobuz')) as app:
    app.start()
