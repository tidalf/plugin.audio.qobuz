'''
    qobuz.i8n
    ~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import gettext
gettext.bindtextdomain('qobuz', 'po/')
gettext.textdomain('qobuz')
_ = gettext.gettext
