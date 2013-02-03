__all__ = ['makeItem']
import sys
from xbmcpy.mock.xbmcaddon import xbmcaddon
from xbmcpy.mock.xbmcplugin import xbmcplugin
from xbmcpy.mock.xbmcgui import xbmcgui

def makeListItemDefault(node):
    label = node.get_label()
#    print "Label %s" % (label)
    image = node.get_image()
    url = u'%s%s' % (xbmcaddon.Addon().getAddonInfo('id'), node.url())
    item = xbmcgui.ListItem(label, label, image, image, url)
    return item

def makeListItem(node):
#    try:
        return makeListItemDefault(node)
#    except Exception as e:
#        print "Cannot make item %s" % (e)
#    return None

def makeItem(node, handle=0):
    return makeListItem(node)

class Setting():
    def get(self, key):
        return xbmcaddon.Addon().getSetting(key)

settings = Setting()