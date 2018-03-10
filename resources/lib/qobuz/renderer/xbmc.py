'''
    qobuz.renderer.xbmc
    ~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from kodi_six import xbmcplugin  # pylint:disable=E0401

from qobuz import config
from qobuz import exception
from qobuz.alarm import Notifier
from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.gui.directory import Directory
from qobuz.gui.util import notifyH
from qobuz.node import getNode, helper
from qobuz.node.flag import Flag
from qobuz.renderer.irenderer import IRenderer
from qobuz.util.common import Struct

logger = getLogger(__name__)
notifier = Notifier(title='Scanning progress')

_kodi_directory_methods = [
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


def helper_kodi_directory_setup(kodi_directory, content_type):
    kodi_directory.set_content(content_type)
    for method in _kodi_directory_methods:
        xbmcplugin.addSortMethod(handle=config.app.handle,
                                 sortMethod=method)


def cyclic_progress(opt):
    opt.count += 1
    if opt.count >= 100:
        opt.count = 0
    return opt.count


def progress_update(scan, heading, message, percent):
    scan.progress.update(heading=heading, message=message, percent=percent)


def is_track(node):
    return node.nt & Flag.TRACK == Flag.TRACK


def populate_node(node, options):
    options = helper.get_tree_traverse_opts(options)
    return node.populating(options)


def _list_track_helper_populate_album(xdir, album_id):
    album = getNode(Flag.ALBUM,
                    parameters={
                        'nid': album_id,
                        'mode': Mode.SCAN
                    })
    album.populating(helper.TreeTraverseOpts(
        xdir=xdir,
        lvl=1,
        whiteFlag=Flag.TRACK,
        blackFlag=Flag.STOPBUILD))


def _list_track_process_node_other(final_directory, _seen, node):
    options = helper.TreeTraverseOpts(xdir=final_directory,
                                      lvl=1,
                                      whiteFlag=Flag.TRACK,
                                      blackFlag=Flag.STOPBUILD)
    populate_node(node, options)


def _list_track_process_node_track(final_directory, seen, node):
    if node.nid in seen.tracks:
        return
    seen.tracks[node.nid] = 1
    album_id = node.get_album_id()
    if album_id is None or album_id == '':
        logger.error('Track without album_id: %s, label: %s',
                     node,
                     node.get_label())
        return
    if album_id in seen.albums:
        return
    seen.albums[album_id] = 1
    _list_track_helper_populate_album(final_directory, album_id)


def list_track(kodi_directory, stats):
    root = kodi_directory.root
    total = 0
    tmp_directory = Directory(None, asList=True)
    final_directory = Directory(None, asList=True)
    if is_track(root):
        tmp_directory.add_node(root)
    else:
        options = helper.TreeTraverseOpts(
            xdir=tmp_directory,
            lvl=3,
            whiteFlag=Flag.ALL,
            blackFlag=Flag.STOPBUILD)
        populate_node(root, options)
    total = len(tmp_directory.nodes)
    if not total:
        logger.info('NoTrack')
        return []

    progress_update(kodi_directory, 'Begin', '', cyclic_progress(stats))
    seen = Struct(**{
        'albums': {},
        'tracks': {}
    })
    for node in tmp_directory.nodes:
        progress_update(kodi_directory,
                        u'Scanning',
                        node.get_label(),
                        cyclic_progress(stats))
        node.set_parameter('mode', Mode.SCAN)
        if is_track(node):
            _list_track_process_node_track(final_directory, seen, node)
        else:
            _list_track_process_node_other(final_directory, seen, node)

    return final_directory.nodes


class QobuzXbmcRenderer(IRenderer):
    '''Specific renderer for Xbmc
        Parameter:
            node_type: int, node type (node.NodeFlag)
            params: dictionary, parameters passed to our plugin
        * You can set parameter after init (see renderer.Irenderer)
    '''

    def __init__(self,
                 node_type,
                 parameters=None,
                 mode=None,
                 whiteFlag=Flag.ALL,
                 blackFlag=Flag.STOPBUILD,
                 depth=1,
                 asList=False):
        parameters = {} if parameters is None else parameters
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
            logger.warn('Cannot set root node (%s, %s)',
                        self.node_type,
                        self.root.get_parameter('nid'))
            return False
        if self.has_method_parameter():
            return self.execute_method_parameter()
        with Directory(self.root,
                       self.nodes,
                       handle=config.app.handle,
                       showProgress=True,
                       asList=self.asList) as kodi_directory:
            if config.app.registry.get('contextmenu_replaceitems', to='bool'):
                kodi_directory.replaceItems = True
            try:
                options = helper.TreeTraverseOpts(xdir=kodi_directory,
                                                  lvl=self.depth,
                                                  whiteFlag=self.whiteFlag,
                                                  blackFlag=self.blackFlag)
                _ret = populate_node(self.root, options)
            except exception.QobuzError as e:
                kodi_directory.end_of_directory(False)
                logger.warn('Error while populating our directory: %s', e)
                return False
            if not self.asList:
                helper_kodi_directory_setup(kodi_directory,
                                            self.root.content_type)
            return kodi_directory.end_of_directory()

    def scan(self):
        '''Building tree when using Xbmc library scanning
        feature
        '''
        if not self.set_root_node():
            logger.warn('Cannot set root node (%s)', self.node_type)
            return False
        stats = Struct(**{
            'count': 0
        })
        with Directory(self.root,
                       nodes=self.nodes,
                       handle=config.app.handle,
                       asLocalUrl=True,
                       showProgress=True) as kodi_directory:
            kodi_directory.progress.heading = u'Scan'
            tracks = {}
            for track in list_track(kodi_directory, stats):
                tracks.update({track.nid: track})
            if not tracks.keys():
                logger.warn('NoTrackScannedError')
                kodi_directory.end_of_directory()
                return False
            for _nid, track in tracks.items():
                if not is_track(track):
                    continue
                if not track.get_displayable():
                    continue
                progress_update(kodi_directory,
                                u'Add Track',
                                track.get_label(default='Library scan'),
                                cyclic_progress(stats))
                kodi_directory.add_node(track)
            kodi_directory.set_content(self.root.content_type)
            kodi_directory.end_of_directory()
            notifyH('Scanning results',
                    '%s items where scanned' % str(kodi_directory.total_put),
                    mstime=3000)
        return True
