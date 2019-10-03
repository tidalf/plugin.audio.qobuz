import xbmcgui  # pylint:disable=E0401

class Progress(xbmcgui.DialogProgressBG):
    def __init__(self, heading='Qobuz', message=None, enable=True):
        xbmcgui.DialogProgressBG.__init__(self)
        self.heading = heading
        self.message = message
        self.percent = 0
        self.dialog = None
        self.enable = enable
        self.create()

    def create(self, heading=None, message=None):
        if self.enable is False:
            return
        self.heading = heading if heading is not None else self.heading
        self.message = message if message is not None else self.message
        self.dialog = xbmcgui.DialogProgressBG()
        self.dialog.create(heading=self.heading, message=self.message)

    def update(self, percent=None, heading=None, message=None):
        if self.dialog is None:
            return
        self.percent = percent if percent is not None else self.percent
        self.heading = heading if heading is not None else self.heading
        self.message = message
        self.dialog.update(self.percent, self.heading, self.message)

    def close(self):
        if self.dialog is not None:
            self.dialog.close()
            self.dialog = None
