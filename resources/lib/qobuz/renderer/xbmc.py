'''
    qobuz.renderer.xbmc
    ~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
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
from qobuz.util.common import is_track

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


def populate_node(node, options):
    options = helper.get_tree_traverse_opts(options)
    return node.populating(options)


def _list_track_helper_list_child(node):
    with Directory(None, asList=True, asLocalUrl=True) as directory:
        options = helper.TreeTraverseOpts(xdir=directory,
                                          lvl=-1,
                                          whiteFlag=Flag.TRACK,
                                          blackFlag=Flag.STOPBUILD)
        populate_node(node, options)
        for node in directory.nodes:
            if not is_track(node):
                continue
            if not node.get_displayable():
                continue
            yield node


def list_track(root):
    with Directory(None, asList=True, asLocalUrl=True) as tmp_directory:
        options = helper.TreeTraverseOpts(
            xdir=tmp_directory,
            lvl=-1,
            whiteFlag=Flag.TRACK,
            blackFlag=Flag.STOPBUILD)
        populate_node(root, options)
        if not tmp_directory.nodes:
            logger.info('NoTrack')
            return
        seen = {}
        for node in tmp_directory.nodes:
            if node.nid in seen:
                continue
            seen[node.nid] = True
            node.set_parameter('mode', Mode.SCAN)
            for other_node in _list_track_helper_list_child(node):
                yield other_node


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
        with Directory(self.root,
                       nodes=self.nodes,
                       handle=config.app.handle,
                       asLocalUrl=True,
                       showProgress=True) as kodi_directory:
            kodi_directory.progress.heading = u'Qobuz library scan'
            for track in list_track(self.root):
                kodi_directory.add_node(track)
            kodi_directory.set_content(self.root.content_type)
            kodi_directory.end_of_directory()
            notifyH('Scanning results',
                    '{} items where scanned'.format(kodi_directory.total_put),
                    mstime=3000)
        return True
