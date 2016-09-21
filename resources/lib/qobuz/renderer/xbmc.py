'''
    qobuz.renderer.xbmc
    ~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import qobuz  # @UnresolvedImport
from qobuz import debug
from qobuz.renderer.irenderer import IRenderer
from qobuz.gui.util import notifyH, getSetting
from qobuz import exception
from qobuz import config
from qobuz.node.flag import Flag
from qobuz.gui.directory import Directory

class QobuzXbmcRenderer(IRenderer):
    """Specific renderer for Xbmc
        Parameter:
            node_type: int, node type (node.NodeFlag)
            params: dictionary, parameters passed to our plugin
        * You can set parameter after init (see renderer.Irenderer)
    """

    def __init__(self, node_type, params={}, mode=None):
        super(QobuzXbmcRenderer, self).__init__(node_type, params, mode)

    def run(self):
        """Building our tree, creating root node based on our node_type
        """
        if not self.set_root_node():
            debug.warn(self, ("Cannot set root node ({}, {})") %
                (str(self.node_type), str(self.root.get_parameter('nid'))))
            return False
        if self.root.hasWidget:
            return self.root.displayWidget()
        if self.has_method_parameter():
            return self.execute_method_parameter()
        from qobuz.gui.directory import Directory
        Dir = Directory(self.root, self.nodes,
                        withProgress=self.enable_progress)
        Dir.asList = self.asList
        Dir.handle = config.app.handle
        if getSetting('contextmenu_replaceitems', asBool=True):
            Dir.replaceItems = True
        try:
            ret = self.root.populating(Dir,
                                       self.depth,
                                       self.whiteFlag,
                                       self.blackFlag)
        except exception.QobuzError as e:
            Dir.end_of_directory(False)
            Dir = None
            debug.warn(self, "Error while populating our directory: %s" % (repr(e)))
            return False
        if not self.asList:
            import xbmcplugin  # @UnresolvedImport
            Dir.set_content(self.root.content_type)
            methods = [
                xbmcplugin.SORT_METHOD_UNSORTED,
                xbmcplugin.SORT_METHOD_LABEL,
                xbmcplugin.SORT_METHOD_DATE,
                xbmcplugin.SORT_METHOD_TITLE,
                xbmcplugin.SORT_METHOD_VIDEO_YEAR,
                xbmcplugin.SORT_METHOD_GENRE,
                xbmcplugin.SORT_METHOD_ARTIST,
                xbmcplugin.SORT_METHOD_ALBUM,
                xbmcplugin.SORT_METHOD_PLAYLIST_ORDER,
                xbmcplugin.SORT_METHOD_TRACKNUM, ]
            [xbmcplugin.addSortMethod(handle=config.app.handle,
                                      sortMethod=method) for method in methods]
        return Dir.end_of_directory()

    def scan(self):
        """Building tree when using Xbmc library scanning
        feature
        """
        if not self.set_root_node():
            debug.warn(self, "Cannot set root node ('{}')",
                       str(self.node_type))
            return False
        handle = config.app.handle
        Dir = Directory(self.root, self.nodes, withProgress=False)
        Dir.handle = int(sys.argv[1])
        Dir.asList = False
        Dir.asLocalUrl = True
        if self.root.nt & Flag.TRACK == Flag.TRACK:
            self.root.fetch(Dir, None, Flag.TRACK, Flag.NONE)
            Dir.add_node(self.root)
        else:
            self.root.populating(Dir, self.depth,
                                 self.whiteFlag, self.blackFlag)
        Dir.set_content(self.root.content_type)
        Dir.end_of_directory()
        notifyH('Scanning results',
                '%s items where scanned' % str(Dir.total_put),
                mstime=3000)
        debug.info(self, 'scanning result total_put: {}', str(Dir.total_put))
        return True
