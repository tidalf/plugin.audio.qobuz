'''
    qobuz.node.inode
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys
from time import time
import urllib
import weakref
import random

from qobuz.api import api
from qobuz.api.user import current as current_user
from qobuz.cache import cache
from qobuz.constants import Mode
from qobuz import exception
from qobuz.gui.contextmenu import contextMenu
from qobuz.gui.util import lang, runPlugin, containerUpdate
from qobuz.gui.util import getImage
from qobuz.api.user import current as user
from qobuz.node import Flag
from qobuz.node import getNode
import qobuz
from qobuz.renderer import renderer
from qobuz.storage import _Storage
from qobuz import config
from qobuz.util import data as dataUtil
from qobuz.util import common
from qobuz.theme import theme, color
from qobuz.util.converter import converter
from qobuz import config
from qobuz.debug import getLogger
logger = getLogger(__name__)

_paginated = [
    'albums', 'labels', 'tracks', 'artists', 'playlists', 'playlist',
    'public_playlists', 'genres'
]


def addint(*a):
    return sum(int(s) for s in a)


class INode(object):
    '''Our base node, every node must inherit or mimic is behaviour

        Calling build_down on a node start the build process
            - pre_build_down: Retrieve data (disk, internet...) and store
                result in self.data
            - _build_down: If pre_build_down return true, parse data
                and populate our node with childs
        The main build_down method is responsible for the logic flow
        (recursive, depth, whiteFlag, blackFlag...)
    '''

    def __init__(self, parent=None, parameters={}, data=None):
        '''Constructor
        @param parent=None: Parent node if not None
        @param parameters={}: dictionary
        '''
        self._nid = None
        self._parent = None
        self._content_type = None
        self._data = None
        self._label = None
        self.parameters = parameters
        self.nt = None
        self.parent = parent
        self.content_type = 'files'
        self.image = None
        self.childs = []
        self.label = None
        self.label2 = None
        self.is_folder = True
        self.pagination_next = None
        self.pagination_prev = None
        self.offset = self.get_parameter('offset', default=0)
        self.hasWidget = False
        self.user_storage = None
        self.nid = self.get_parameter('nid', default=None) \
            or self.get_property('id', default=None)
        self.data = data
        self.node_storage = None
        self.user_storage = None
        self.limit = config.app.registry.get('pagination_limit', to='int')
        self.mode = self.get_parameter('mode', to='int')

    def set_nid(self, value):
        '''@setter nid'''
        self._nid = value

    def get_nid(self):
        '''@getter nid'''
        if self._data and 'id' in self._data:
            return self._data['id']
        return self._nid

    nid = property(get_nid, set_nid)

    def get_parent(self):
        '''@getter parent'''
        if self._parent is None:
            return None
        return self._parent

    def set_parent(self, parent):
        '''@setter parent'''
        if parent is None:
            self._parent = None
            return
        self._parent = parent

    parent = property(get_parent, set_parent)

    def get_content_type(self):
        '''@getter content_type'''
        return self._content_type

    def set_content_type(self, kind):
        '''@setter content_type'''
        if kind not in [
                'files', 'songs', 'artists', 'albums', 'movies', 'tvshows',
                'episodes', 'musicvideos'
        ]:
            raise exception.InvalidKind(kind)
        self._content_type = kind

    content_type = property(get_content_type, set_content_type)

    def get_data(self):
        return self._data

    def set_data(self, value):
        self._data = value
        self.hook_post_data()

    data = property(get_data, set_data)

    def hook_post_data(self):
        ''' Called after node data is set '''
        pass

    def set_property(self, pathList, value):
        if self.data is None:
            raise KeyError('Node without data')
        root = self.data
        for part in pathList.split('/'):
            if part not in root:
                root[part] = {}
            root = root[part]
        root = value

    def get_property(self, pathList, default=u'', to='raw'):
        '''Property are just a easy way to access JSON data (self.data)
        @param pathList: a string or a list of string, each string can be
            a path like 'album/image/large'
        @return: string (empty string when all fail or when there's no data)
            * When passing array of string the method return the first
            path returning data

        Example:
            image = self.get_property(['image/extralarge',
                                   'image/mega',
                                   'picture'])
        '''
        if isinstance(pathList, basestring):
            res = self.__get_property(pathList)
            if res is None:
                return default
            return getattr(converter, to)(res)
        for path in pathList:
            data = self.__get_property(path)
            if data is not None:
                return getattr(converter, to)(data)
        return default

    def __get_property(self, path):
        '''Helper used by get_property method
        '''
        if self.data is None:
            return None
        xPath = path.split('/')
        root = self.data
        for i in range(0, len(xPath)):
            if not xPath[i] in root:
                return None
            root = root[xPath[i]]
            if common.is_empty(root):
                return None
        if root is not None and root != 'None':
            return root
        return None

    def __add_pagination(self, data):
        '''build_down helper: Add pagination data when needed
        '''
        if not data:
            return False
        items = None
        for kind in _paginated:
            if kind in data and data[kind]:
                items = data[kind]
                break
        if items is None:
            return False
        if 'limit' not in items or 'total' not in items:
            return False
        if items['limit'] is None:
            return False
        newlimit = addint(items['offset'], items['limit'])
        if items['total'] < newlimit:
            return False
        url = self.make_url(offset=newlimit)
        self.pagination_next = url
        self.pagination_total = items['total']
        self.pagination_offset = items['offset']
        self.pagination_limit = items['limit']
        self.pagination_next_offset = newlimit
        return True

    def set_parameters(self, parameters):
        '''Setting parameters property
        @param parameters: Dictionary
        '''
        self.parameters = parameters

    def set_parameter(self, name, value, quote=False, **ka):
        '''Setting a parameter
        @param name: parameter name
        @param value: parameter value
        @param quote=False: use urllib.quote_plus against return value when True
        '''
        if quote is True:
            value = urllib.quote_plus(value)
        self.parameters[name] = value

    def get_parameter(self, name, default=None, to='raw'):
        '''Getting parameter by name
        @param name: parameter name
        @param default: value set when parameter not found or value is None
        @param to='raw': string, converter used
        '''
        if self.parameters is None:
            return getattr(converter, to)(default)
        if name not in self.parameters:
            return getattr(converter, to)(default)
        value = self.parameters[name]
        if value is None:
            return getattr(converter, to)(default)
        return getattr(converter, to)(value)

    def del_parameter(self, name):
        '''Deleting parameter
        @param name: parameter name
        '''
        if name not in self.parameters:
            return False
        del self.parameters[name]
        return True

    def make_url(self, **ka):
        '''Generate URL to navigate between nodes
            Nodes with custom parameters must override this method
            @todo: Ugly need rewrite =]
        '''
        if 'mode' not in ka:
            ka['mode'] = Mode.VIEW
        if 'nt' not in ka:
            ka['nt'] = self.nt
        if 'nid' not in ka:
            ka['nid'] = self.nid
        if 'offset' not in ka:
            ka['offset'] = self.offset
        if 'asLocalUrl' in ka and not ka['asLocalUrl']:
            del ka['asLocalUrl']
        if 'offset' in ka and ka['offset'] == 0:
            del ka['offset']
        for name in ['qnt', 'qid', 'query', 'search-type', 'mode']:
            if name in ka:
                continue
            value = self.get_parameter(name)
            if value is None:
                continue
            ka[name] = self.get_parameter(name)
        url = sys.argv[0] + '?'
        for key in sorted(ka):
            value = ka[key]
            if value is None:
                continue
            value = str(value).strip()
            if value == '':
                continue
            url += key + '=' + value + '&'
        url = url[:-1]
        return url

    def makeListItem(self, **ka):
        '''
            Make Xbmc List Item
            return  a xbml list item
            Class can overload this method
        '''
        import xbmcgui  # @UnresolvedImport
        if 'url' not in ka:
            ka['url'] = self.make_url()
        if 'label' not in ka:
            ka['label'] = self.get_label()
        if 'label2' not in ka:
            ka['label2'] = self.get_label()
        if 'image' not in ka:
            ka['image'] = self.get_image()
        if 'asLocalUrl' in ka and not ka['asLocalUrl']:
            del ka['asLocalUrl']
        item = xbmcgui.ListItem(ka['label'], ka['label2'], ka['image'],
                                ka['image'], ka['url'])
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), ka['replaceItems'])
        return item

    def add_child(self, child):
        child.parent = self
        child.set_parameters(self.parameters)
        self.childs.append(child)
        return self

    def get_childs(self):
        return self.childs

    def set_label(self, label):
        self._label = label
        return self

    def get_label(self, default=None):
        if self._label is None:
            return default
        return self._label

    label = property(get_label, set_label)

    def get_image(self):
        if self.image:
            return self.image
        if self.parent:
            return self.parent.get_image()
        if self.data is not None:
            for name in ['images300', 'images150', 'images']:
                if name in self.data and len(self.data[name]) > 0:
                    return self.data[name][random.randrange(
                        len(self.data[name]))]
        return self.get_property('image')

    def set_image(self, image):
        self.image = image
        return self

    def get_label2(self):
        return self.label2

    def render_nodes(self,
                     nt,
                     parameters,
                     lvl=1,
                     whiteFlag=Flag.ALL,
                     blackFlag=Flag.TRACK & Flag.STOPBUILD):
        render = renderer(nt, parameters)
        render.depth = -1
        render.whiteFlag = whiteFlag
        render.blackFlag = blackFlag
        render.asList = True
        render.run()
        return render

    def fetch(self, Dir=None, lvl=1, whiteFlag=None, blackFlag=None):
        '''When returning None we are not displaying directory content
        '''
        return {}

    def populating(self,
                   xdir,
                   lvl=1,
                   whiteFlag=Flag.ALL,
                   blackFlag=Flag.NONE,
                   data={}):
        if lvl != -1 and lvl < 1:
            return False
        if self.nt & blackFlag != self.nt:
            new_data = self.fetch(xdir, lvl, whiteFlag, blackFlag)
            if new_data is None:
                return False
            data.update(new_data)
            self.data = data
            self.__add_pagination(self.data)
        self.populate(xdir, lvl, whiteFlag, blackFlag)
        if lvl != -1:
            lvl -= 1
        self.__add_pagination_node(xdir, lvl, whiteFlag)
        for child in self.childs:
            if child.nt & whiteFlag == child.nt:
                if not xdir.add_node(child):
                    logger.error('Could not add node')
                    continue
            child.populating(xdir, lvl, whiteFlag, blackFlag)

    def populate(self,
                 xbmc_directory=None,
                 lvl=-1,
                 whiteFlag=Flag.ALL,
                 blackFlag=Flag.STOPBUILD):
        '''Hook / _build_down:
        This method is called by build_down, each object who
        inherit from Inode can overide it. Lot of object
        simply fetch data from qobuz (cached data)
        '''
        pass

    def __add_pagination_node(self, Dir, lvl=1, whiteFlag=Flag.NODE):
        """Helper/Called by build_down to add special node when pagination is
        required
        """
        if self.pagination_next:
            colorItem = theme.get('item/default/color')
            params = config.app.bootstrap.params
            params['offset'] = self.pagination_next_offset
            params['nid'] = self.nid
            node = getNode(self.nt, params)
            node.data = self.data
            node.label = u'{label} [{next_offset} / {pagination_total}]'.format(
                label=self.get_label(),
                next_offset=self.pagination_next_offset,
                pagination_total=self.pagination_total)
            self.add_child(node)

    def attach_context_menu(self, item, menu):
        '''Note: Url made with make_url must set mode (like mode=Mode.VIEW)
            else we are copying current mode (for track it's Mode.PLAY ...)
        '''
        ''' HOME '''
        colorCaution = theme.get('item/caution/color')

        def c_pl(txt):
            return color(theme.get('menu/playlist/color'), txt)

        def c_fav(txt):
            return color(theme.get('menu/favorite/color'), txt)

        url = self.make_url(nt=Flag.ROOT, mode=Mode.VIEW, nm='')
        menu.add(path='qobuz',
                 label="Qobuz",
                 cmd=containerUpdate(url, False),
                 id='',
                 pos=-5)
        ''' ARTIST '''
        if self.nt & (Flag.ALBUM | Flag.TRACK | Flag.ARTIST):
            artist_id = self.get_artist_id()
            artist_name = self.get_artist()
            urlArtist = self.make_url(
                nt=Flag.ARTIST, nid=artist_id, mode=Mode.VIEW)
            menu.add(path='artist/all_album',
                     label="%s %s" % (lang(30157), artist_name),
                     cmd=containerUpdate(urlArtist),
                     pos=-10)
            ''' Similar artist '''
            url = self.make_url(
                nt=Flag.SIMILAR_ARTIST, nid=artist_id, mode=Mode.VIEW)
            menu.add(path='artist/similar',
                     label=lang(30160),
                     cmd=containerUpdate(url))
        ''' FAVORITES '''
        wf = self.nt & (~Flag.FAVORITE)
        if self.parent:
            wf = wf and self.parent.nt & ~Flag.FAVORITE
        if wf:
            ''' ADD TO FAVORITES / TRACKS'''
            url = self.make_url(nt=Flag.FAVORITE, nm='', mode=Mode.VIEW)
            menu.add(path='favorites',
                     label=c_fav("Favorites"),
                     cmd=containerUpdate(url, True),
                     pos=-9)
            url = self.make_url(
                nt=Flag.FAVORITE,
                nm='gui_add_tracks',
                qid=self.nid,
                qnt=self.nt,
                mode=Mode.VIEW)
            menu.add(path='favorites/add_tracks',
                     label=c_fav(lang(30167) + ' tracks'),
                     cmd=runPlugin(url))
            ''' ADD TO FAVORITES / Albums'''
            url = self.make_url(
                nt=Flag.FAVORITE,
                nm='gui_add_albums',
                qid=self.nid,
                qnt=self.nt,
                mode=Mode.VIEW)
            menu.add(path='favorites/add_albums',
                     label=c_fav(lang(30167) + ' albums'),
                     cmd=runPlugin(url))
            # ''' ADD TO FAVORITES / Artists'''
            # url = self.make_url(
            #     nt=Flag.FAVORITE,
            #     nm='gui_add_artists',
            #     qid=self.nid,
            #     qnt=self.nt,
            #     mode=Mode.VIEW)
            # menu.add(path='favorites/add_artists',
            #          label=c_fav(lang(30167) + ' artists'),
            #          cmd=runPlugin(url))

        if self.parent and (self.parent.nt & Flag.FAVORITE):
            url = self.make_url(nt=Flag.FAVORITE, nm='', mode=Mode.VIEW)
            menu.add(path='favorites',
                     label="Favorites",
                     cmd=containerUpdate(url, True),
                     pos=-9)
            url = self.make_url(
                nt=Flag.FAVORITE,
                nm='gui_remove',
                qid=self.nid,
                qnt=self.nt,
                mode=Mode.VIEW)
            menu.add(path='favorites/remove',
                     label=c_fav('Remove %s' % (self.get_label())),
                     cmd=runPlugin(url),
                     color=colorCaution)
        wf = ~Flag.USERPLAYLISTS
        if wf:
            ''' PLAYLIST '''
            cmd = containerUpdate(
                self.make_url(
                    nt=Flag.USERPLAYLISTS, nid='', mode=Mode.VIEW))
            menu.add(path='playlist',
                     pos=1,
                     label=c_pl("Playlist"),
                     cmd=cmd,
                     mode=Mode.VIEW)
            ''' ADD TO CURRENT PLAYLIST '''
            cmd = runPlugin(
                self.make_url(
                    nt=Flag.PLAYLIST,
                    nm='gui_add_to_current',
                    qnt=self.nt,
                    mode=Mode.VIEW,
                    qid=self.nid))
            menu.add(path='playlist/add_to_current',
                     label=c_pl(lang(30161)),
                     cmd=cmd)
            label = self.get_label()
            try:
                label = label.encode('utf8', 'replace')
            except:
                logger.warn('Cannot set query... %s', repr(label))
                label = ''
            label = urllib.quote_plus(label)
            ''' ADD AS NEW '''
            cmd = runPlugin(
                self.make_url(
                    nt=Flag.PLAYLIST,
                    nm='gui_add_as_new',
                    qnt=self.nt,
                    query=label,
                    mode=Mode.VIEW,
                    qid=self.nid))
            menu.add(path='playlist/add_as_new',
                     label=c_pl(lang(30082)),
                     cmd=cmd)
        ''' PLAYLIST / CREATE '''
        cFlag = (Flag.PLAYLIST | Flag.USERPLAYLISTS)
        if self.nt | cFlag == cFlag:
            cmd = runPlugin(
                self.make_url(
                    nt=Flag.PLAYLIST, nm="gui_create", mode=Mode.VIEW))
            menu.add(path='playlist/create', label=c_pl(lang(30164)), cmd=cmd)
        # ''' VIEW BIG DIR '''
        # cmd = containerUpdate(self.make_url(mode=Mode.VIEW_BIG_DIR))
        # menu.add(path='qobuz/big_dir', label=lang(30158), cmd=cmd)
        if config.app.registry.get('enable_scan_feature', to='bool'):
             ''' SCAN'''
             query = urllib.quote_plus(
                 self.make_url(
                     mode=Mode.SCAN, asLocalUrl=True))
             url = self.make_url(
                 nt=Flag.ROOT, mode=Mode.VIEW, nm='gui_scan', query=query)
             menu.add(path='qobuz/scan', cmd=runPlugin(url), label='scan')
        if self.nt & (Flag.ALL & ~Flag.ALBUM & ~Flag.TRACK & ~Flag.PLAYLIST):
            ''' ERASE CACHE '''
            cmd = runPlugin(
                self.make_url(
                    nt=Flag.ROOT, nm="cache_remove", mode=Mode.VIEW))
            menu.add(path='qobuz/erase_cache',
                     label=lang(30117),
                     cmd=cmd,
                     color=colorCaution,
                     pos=10)
            if config.app.registry.get('enable_scan_feature', to='bool'):
                ''' HTTP / Kooli '''
                cmd = runPlugin(
                    self.make_url(
                        nt=Flag.TESTING, nm="show_dialog", mode=Mode.VIEW))
                menu.add(path='qobuz/test httpd',
                         label='Test web service',
                         cmd=cmd,
                         pos=11)

    def get_user_storage(self):
        if self.user_storage is not None:
            return self.user_storage
        filename = os.path.join(cache.base_path,
                                'user-%s.local' % str(current_user.get_id()))
        self.user_storage = _Storage(filename)
        return self.user_storage

    def get_user_path(self):
        return os.path.join(cache.base_path)

    def get_user_data(self):
        data = api.get('/user/login',
                       username=user.username,
                       password=user.password)
        if not data:
            return None
        return data['user']

    def get_class_name(self):
        return self.__class__.__name__

    def as_dict(self):
        d = {}
        for k in ['class_name', 'nid', 'parent']:
            d[k] = getattr(self, 'get_%s' % k)()
        return d

    def __str__(self):
        return '<{class_name} nid={nid}>'.format(**self.as_dict())

    def get_node_storage_path(self):
        return os.path.join(cache.base_path, self._get_node_storage_filename())

    def get_node_storage(self):
        if self.node_storage is not None:
            return self.node_storage
        self.node_storage = _Storage(self.get_node_storage_path())
        return self.node_storage

    def remove_node_storage(self):
        filename = self.get_node_storage_path()
        if os.path.exists(filename):
            os.unlink(filename)

    def _get_node_storage_filename(self):
        raise NotImplmentedError()

    def remove_playlist_storage():
        path = os.path.join(cache.base_path, self._get_node_storage_filename())
        if os.path.exists(path):
            os.unlink(path)

    def get_image_from_storage(self):
        desired_size = config.app.registry.get('image_default_size',
                                               default=None)
        images = []
        if self.nid is not None:
            storage = self.get_node_storage()
            if storage is not None:
                images_len = 0
                if 'image' not in storage:
                    images = dataUtil.list_image(
                        self.data, desired_size=desired_size)
                    images_len = len(images)
                    if images_len > 0:
                        storage['image'] = images
                        storage.sync()
                else:
                    images = storage['image']
                images_len = len(images)
                if images_len > 0:
                    return images[random.randrange(0, images_len, 1)]
            else:
                logger.error('Cannot get node storage')
        return None

    def count(self):
        if self.data is None:
            raise exception.NodeHasNoData(Flag.to_s(self.nt))
        if not hasattr(self, '_count'):
            raise exception.NodeHasNoCountMethod(Flag.to_s(self.nt))
        return getattr(self, '_count')()
