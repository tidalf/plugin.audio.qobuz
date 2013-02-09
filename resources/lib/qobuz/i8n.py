'''
    qobuz.i8n
    ~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import gettext
for name in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
    if not name in os.environ:
        continue
    print "%s: %s" % (name, os.environ[name])
local_path = os.path.dirname(os.path.abspath(__file__))
print "Local path: %s" % local_path
gettext.bindtextdomain('qobuz', os.path.join(local_path, 'locale'))
gettext.textdomain('qobuz')
_ = gettext.gettext
