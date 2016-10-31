import xbmcgui

from qobuz import debug

class Progress(xbmcgui.DialogProgressBG):

    def __init__(self, heading='Qobuz', message=None):
        xbmcgui.DialogProgressBG.__init__(self)
        self.heading = heading
        self.message = message

    def create(self, heading=None, message=None):
        self.heading = heading if heading is not None else self.heading
        self.message = message if message is not None else self.message
        xbmcgui.DialogProgressBG.create(self, self.heading, self.message)
