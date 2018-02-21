import xbmcgui
from qobuz.debug import getLogger
logger = getLogger(__name__)


class DialogSelect(object):
    def __init__(self, label='Select', items=[]):
        self.label = label
        self.ret = -1
        self.items = items

    def open(self):
        self.ret = -1
        try:
            self.ret = xbmcgui.Dialog().select(self.label, self.items)
        except Exception as e:
            logger.error('Error: %s', e)
        return self.ret
