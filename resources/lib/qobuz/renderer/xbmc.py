'''
    qobuz.renderer.xbmc
    ~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import xbmcplugin
import qobuz
from qobuz import debug
from qobuz.renderer.irenderer import IRenderer
from qobuz.gui.util import notifyH
from qobuz import exception
from qobuz import config
from qobuz.node.flag import Flag
from qobuz.constants import Mode
from qobuz.node import getNode
from qobuz.gui.directory import Directory
from qobuz.alarm import Notifier
from qobuz.gui.bg_progress import Progress

notifier = Notifier(title='Scanning progress')


class QobuzXbmcRenderer(IRenderer):
    '''Specific renderer for Xbmc
        Parameter:
            node_type: int, node type (node.NodeFlag)
            params: dictionary, parameters passed to our plugin
        * You can set parameter after init (see renderer.Irenderer)
    '''

    def __init__(self,
                 node_type,
                 parameters={},
                 mode=None,
                 whiteFlag=Flag.ALL,
                 blackFlag=Flag.STOPBUILD,
                 depth=1,
                 asList=False):
        super(QobuzXbmcRenderer, self).__init__(
            node_type,
            parameters=parameters,
            mode=mode,
            whiteFlag=whiteFlag,
            blackFlag=blackFlag,
            depth=depth,
            asList=asList)

    def run(self):
        '''Building our tree, creating root node based on our node_type
        '''
        if not self.set_root_node():
            debug.warn(self, 'Cannot set root node ({}, {})',
                       str(self.node_type),
                       str(self.root.get_parameter('nid')))
            return False
        if self.has_method_parameter():
            return self.execute_method_parameter()
        with Directory(
                self.root,
                self.nodes,
                handle=config.app.handle,
                showProgress=True,
                asList=self.asList) as xdir:
            if config.app.registry.get('contextmenu_replaceitems', to='bool'):
                xdir.replaceItems = True
            try:
                ret = self.root.populating(xdir, self.depth, self.whiteFlag,
                                           self.blackFlag)
            except exception.QobuzError as e:
                xdir.end_of_directory(False)
                xdir = None
                debug.warn(self, 'Error while populating our directory: %s' %
                           (repr(e)))
                return False
            if not self.asList:
                xdir.set_content(self.root.content_type)
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
                    xbmcplugin.SORT_METHOD_TRACKNUM,
                ]
                [
                    xbmcplugin.addSortMethod(
                        handle=config.app.handle, sortMethod=method)
                    for method in methods
                ]
            return xdir.end_of_directory()

    def scan(self):
        '''Building tree when using Xbmc library scanning
        feature
        '''
        if not self.set_root_node():
            debug.warn(self, 'Cannot set root node ({})', str(self.node_type))
            return False

        def list_track(scan):
            root = scan.root
            total = 0
            predir = Directory(None, asList=True)
            findir = Directory(None, asList=True)
            if root.nt & Flag.TRACK == Flag.TRACK:
                predir.add_node(root)
            else:
                root.populating(predir, 3, Flag.ALL, Flag.STOPBUILD)
            total = len(predir.nodes)
            if total == 0:
                return []
            done = 0

            def percent():
                return (done / total) * 100

            scan.progress.update(message='Begin', percent=percent())
            seen = {}
            seen_tracks = {}
            for node in predir.nodes:
                scan.progress.update(
                    percent(),
                    'Scanning',
                    node.get_label().encode(
                        'ascii', errors='ignore'))
                done += 1
                node.set_parameter('mode', Mode.SCAN)
                if node.nt & Flag.TRACK == Flag.TRACK:
                    if node.nid in seen_tracks:
                        continue
                    seen_tracks[node.nid] = 1
                    album_id = node.get_album_id()
                    if album_id is None or album_id == '':
                        debug.error(
                            self,
                            'Track without album_id: {}, label: {}',
                            node,
                            node.get_label().encode(
                                'ascii', errors='ignore'))
                        continue
                    if album_id in seen:
                        continue
                    seen[album_id] = 1
                    album = getNode(
                        Flag.ALBUM,
                        parameters={'nid': album_id,
                                    'mode': Mode.SCAN})
                    album.populating(findir, 1, Flag.TRACK, Flag.STOPBUILD)
                else:
                    node.populating(findir, 1, Flag.TRACK, Flag.STOPBUILD)
            return findir.nodes

        with Directory(
                self.root,
                nodes=self.nodes,
                handle=config.app.handle,
                asLocalUrl=True,
                showProgress=True) as xdir:
            xdir.progress.heading = 'Scan (i8n)'
            tracks = {}
            d = {}
            for track in list_track(xdir):
              d[track.nid] = track
            tracks.update(d)
            if len(tracks.keys()) == 0:
                xdir.end_of_directory()
                return False
            for nid, track in tracks.items():
                if track.nt & Flag.TRACK != Flag.TRACK:
                    continue
                if not track.get_displayable():
                    continue
                xdir.add_node(track)
            xdir.set_content(self.root.content_type)
            xdir.end_of_directory()
            notifyH(
                'Scanning results',
                '%s items where scanned' % str(xdir.total_put),
                mstime=3000)
        return True
