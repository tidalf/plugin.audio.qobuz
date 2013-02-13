from xbmcpy.mock.xbmcplugin import xbmcplugin
import xbmcpy.mock.xbmcaddon as xbmcaddon
from xbmcpy.mock.xbmcgui import xbmcgui
from node import Mode
from qobuz.node import Flag
from node.renderer.base import BaseRenderer

class ItemFactory(object):

    def make_item(self, node):
        if node is None:
            return None
        label = node.get_label()
        image = node.get_image()
        plugin_id = xbmcaddon.Addon().getAddonInfo('id')
        url = '%s%s' % (plugin_id, node.url())
        item = xbmcgui.ListItem(label, label, image, image, url)
        return item
        return None

from qobuz.exception import QobuzException

class AppendItemError(QobuzException):
    pass

class XbmcRenderer(BaseRenderer):

    def __init__(self, plugin, commander, itemFactory, player=None):
        self.itemFactory = itemFactory
        self.plugin = plugin
        self.commander = commander
        self.alive = True
        self.stack_env = []
        self.player = player
        self.depth = 1
        self.whiteFlag = Flag.ALL
        self.blackFlag = Flag.TRACK

    def append(self, node):
        handle = self.plugin.handle
        item = self.itemFactory.make_item(node)
        if item:
            url = self.plugin.base_url + node.url()
            if not xbmcplugin.addDirectoryItem(handle, url, item, 
                                        node.is_folder, 1):
                raise AppendItemError()
        else:
            print "No item... @#!"
        return super(XbmcRenderer, self).append(node)

    def render(self, node):
        print node.pretty(Flag)
        self.alive = False
        if self.commander.has_action(node):
            ret = self.commander.execute(node)
            self.end(ret)
            return ret
        if node.get_parameter('mode', number=True) == Mode.PLAY:
            if not node.fetch():
                return False
            if self.player and node.is_playable:
                self.alive = False
                return self.player.play(self, node)
            return False
        self.clear()
        try:
            node.populating(self)
        except AppendItemError as e:
            print "Operation canceled"
            self.clear()
        except Exception as e:
            raise e
        return self.end()

    def ask(self):
        pass

    def end(self, succeeded=None):
        handle = self.plugin.handle
        if succeeded is None:
            succeeded = True if len(self) > 0 else False
        updateListing= not succeeded
        cacheToDisc=succeeded
        xbmcplugin.endOfDirectory(handle, succeeded, updateListing, 
                                  cacheToDisc)
        return True
