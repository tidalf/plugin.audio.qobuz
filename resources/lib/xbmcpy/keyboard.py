'''
    xbmcpy.keyboard
    ~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
__all__ = ['Keyboard']

Keyboard = None

try:
    import xbmc # @UnresolvedImport
    Keyboard = xbmc.Keyboard
except:
    from console import console

    class _Keyboard_():
        
        def __init__(self, default, heading, ktype):
            self.heading = heading
            self.ktype = ktype

        def doModal(self):
            self.inp = console.raw_input('%s >' % (self.heading))

        def isConfirmed(self):
            if self.inp:
                return True
            return False

        def getText(self):
            print "Input: %s" % (self.inp)
            return self.inp

    Keyboard = _Keyboard_
