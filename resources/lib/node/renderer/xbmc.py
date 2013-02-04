from xbmcpy.mock.xbmcplugin import xbmcplugin
import xbmcpy.mock.xbmcaddon as xbmcaddon
from xbmcpy.mock.xbmcgui import xbmcgui
from node import Mode

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

class Commander(object):

    def __init__(self, flag):
        self.flag = flag

    def has_action(self, plugin, node):
        if plugin.parameter('action'):
            return True
        return False

    def execute(self, plugin, node):
        action = plugin.parameter('action')
        if not action:
            return True
        del node.parameters['action']
        print "Executing action %s on %s" % (action, node)
        nodename = self.flag.to_s(node.kind)
        return getattr(self, 'action_%s_%s' % (nodename, action))(plugin, node)


from collections import deque

class XbmcRenderer(deque):

    def __init__(self):
        self.itemFactory = ItemFactory()
        self.alive = True
        self.stack_env = []
        self.plugin = None
        self.player = None
        self.depth = 1
        self.whiteFlag = None
        self.handle = None
        self.commander = None

    def append(self, node):
        item = self.itemFactory.make_item(node)
        if item:
            url = self.plugin.base_url + node.url()
            xbmcplugin.addDirectoryItem(self.handle, url, item, 
                                        node.is_folder, 1)
        else:
            print "No item... @#!"
        return super(XbmcRenderer, self).append(node)

    def render(self, plugin, node):
        self.alive = False
        if self.commander:
            if self.commander.has_action(plugin, node):
                ret = self.commander.execute(plugin, node)
                self.end()
                return ret
        print "[Qobuz] Renderer starting\nnode %s" % (node)
        if plugin.parameter('mode') == str(Mode.PLAY):
            if self.player and node.is_playable:
                print "Playing track %s" % (node.get_label())
                self.alive = False
                return self.player.play(self, node)
        self.clear()
        self.plugin = plugin
        self.handle = plugin.handle()
        node.populating(self, self.depth, self.whiteFlag)
        return self.end()

    def ask(self):
        pass

    def end(self):
        handle = self.handle
        succeeded = True if len(self) > 0 else False
        updateListing=not succeeded
        cacheToDisc=succeeded
        xbmcplugin.endOfDirectory(handle, succeeded, updateListing, 
                                  cacheToDisc)
        return True
