class Mock(object):

    def __init__(self):
        self.items = []

    def ListItem(self, label, label2=None, image=None, thumb=None, url=None):
        self.items.append((label, label2, image, thumb, url))

try:
    import xbmcgui
except:
    xbmcgui = Mock()

