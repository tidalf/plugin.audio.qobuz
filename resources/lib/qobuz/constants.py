'''
    qobuz.constants
    ~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
__debugging__ = 0

class __Mode():

    def __init__(self):
        self.VIEW = 1
        self.PLAY = 2
        self.SCAN = 3
        self.VIEW_BIG_DIR = 4

    def to_s(self, mode):
        if mode == self.VIEW:
            return "view"
        elif mode == self.PLAY:
            return "play"
        elif mode == self.SCAN:
            return "scan"
        elif mode == self.VIEW_BIG_DIR:
            return "view big dir"
        else:
            return "Unknow mode: " + str(mode)

Mode = __Mode()
