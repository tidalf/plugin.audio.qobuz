'''
    default (XBMC addon entry point)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import os
import traceback
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             'resources', 'lib'))

from qobuz.plugin import Plugin
from qobuz.application import Application
from qobuz import debug

try:
    app = Application(Plugin('plugin.audio.qobuz'))
    app.start()
except Exception as e:
    debug.error(__name__, 'Error: {}', e)
    traceback.print_exc()
