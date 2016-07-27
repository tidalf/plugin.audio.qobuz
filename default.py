'''
    default (XBMC addon entry point)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

import os
import sys

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resources', 'lib'))

from qobuz.plugin import Plugin
from qobuz.application import Application

app = Application(Plugin('plugin.audio.qobuz'))
app.start()
