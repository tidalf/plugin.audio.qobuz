from xbmcpy.mock.xbmcplugin import xbmcplugin
import xbmcpy.mock.xbmcaddon as xbmcaddon
from xbmcpy.mock.xbmcgui import xbmcgui
from pyobuz.node.ibase import Mode
from pyobuz.node import Flag
from pyobuz.renderer.base import BaseRenderer
from pyobuz.debug import log, warn
from pyobuz.exception import AppendItemError


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
        self.content_type = 'albums'

    def append(self, node):
        handle = self.plugin.handle
        item = self.itemFactory.make_item(node)
        if item:
            url = self.plugin.base_url + node.url()
            if not xbmcplugin.addDirectoryItem(handle, url, item,
                                        node.is_folder, 1):
                raise AppendItemError()
        else:
            warn(self, "No item... @#!")
        return super(XbmcRenderer, self).append(node)

    def render(self, node):
        self.alive = False
        if self.commander.has_action(node):
            succeeded, cache, update = self.commander.execute(self, node)
            self.end(succeeded=succeeded, cacheToDisc=cache,
                     updateListing=update)
            return succeeded
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
            self.content_type = node.content_type
        except AppendItemError as _e:
            print "Operation canceled"
            self.clear()
        return self.end()

    def ask(self):
        pass

    def end(self, succeeded=True, cacheToDisc=True, updateListing=False):
        handle = self.plugin.handle
        log(self, "Set content_type: %s" % self.content_type)
        xbmcplugin.setContent(handle, self.content_type)
        xbmcplugin.endOfDirectory(handle, succeeded, updateListing,
                                  cacheToDisc)
        return True
