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
from qobuz.cache import cache
from qobuz.constants import Mode
from qobuz import debug
from qobuz import exception
from qobuz.gui.contextmenu import contextMenu
from qobuz.gui.util import color, lang, runPlugin, containerUpdate, getSetting
from qobuz.gui.util import getImage
from qobuz.node import Flag
from qobuz.node import getNode
import qobuz  # @UnresolvedImport
from qobuz.renderer import renderer
from qobuz.storage import _Storage
from qobuz import config
from qobuz.util import data as dataUtil
from qobuz.util import common

class Converter(object):

    def raw(self, data, default=None):
        return data

    def string(self, data, default=None):
        if data is None:
            return default
        return str(data)

    def int(self, data, default=None):
        if common.is_empty(data):
            return default
        return int(data)

    def float(self, data, default=None):
        if common.is_empty(data):
            return default
        return float(data)
    def bool(self, data, default=None):
        return common.input2bool(data)

    def unquote(self, data, default=None):
        if data is None:
            return default
        return urllib.unquote_plus(data)

    def quote(self, data, default=None):
        if data is None:
            return default
        return urllib.quote_plus(data)

converter = Converter()
_paginated = ['albums', 'labels', 'tracks', 'artists',
                     'playlists', 'playlist', 'public_playlists', 'genres']
class INode(object):
    '''Our base node, every node must inherit or mimic is behaviour

        Calling build_down on a node start the build process
            - pre_build_down: Retrieve data (disk, internet...) and store
                result in self.data
            - _build_down: If pre_build_down return true, parse data
                and populate our node with childs
        The main build_down method is responsible for the logic flow (recursive,
            depth, whiteFlag, blackFlag...)
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
        self.label = ''
        self.label2 = None
        self.is_folder = True
        self.pagination_next = None
        self.pagination_prev = None
        self.offset = self.get_parameter('offset') or 0
        self.hasWidget = False
        self.user_storage = None
        self.nid = self.get_parameter('nid', default=None) or self.get_property('id', default=None)
        self.data = data
        self.node_storage = None
        self.limit = getSetting('pagination_limit')
        self.mode = self.get_parameter('mode')

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
        return self._parent()

    def set_parent(self, parent):
        '''@setter parent'''
        if parent is None:
            self._parent = None
            return
        self._parent = weakref.ref(parent)

    parent = property(get_parent, set_parent)

    def delete_tree(self):
        '''Recursive delete
        '''
        if self.childs is not None:
            for child in self.childs:
                child.delete_tree()
        self.childs = None
        self.parent = None
        self.parameters = None


    def get_content_type(self):
        '''@getter content_type'''
        return self._content_type

    def set_content_type(self, kind):
        '''@setter content_type'''
        if kind not in ['files', 'songs', 'artists', 'albums', 'movies',
                        'tvshows', 'episodes', 'musicvideos']:
            raise exception.InvalidKind(kind)
        self._content_type = kind

    content_type = property(get_content_type, set_content_type)

    def get_data(self):
        '''@getter data'''
        return self._data

    def set_data(self, value):
        '''@setter data'''
        self._data = value
        self.hook_post_data()

    data = property(get_data, set_data)

    def hook_post_data(self):
        ''' Called after node data is set '''
        pass

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
            return res if res is not None else default
        for path in pathList:
            data = self.__get_property(path)
            if data is not None:
                return getattr(converter, to)(data)
        return getattr(converter, to)(default)

    def __get_property(self, path):
        '''Helper used by get_property method
        '''
        if self.data is None:
            return None
        xPath = path.split('/')
        root = self.data
        for i in range(0, len(xPath)):
            if not xPath[i] in root:
                #debug.warn(self, 'Invalid property path {} in {}', path, xPath[i])
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
        need_pagination = False
        for p in _paginated:
            if p not in data or data[p] is None:
                continue
            items = data[p]
            if 'limit' not in items or 'total' not in items:
                continue
            if items['limit'] is None:
                continue
            if items['total'] > (items['offset'] + items['limit']):
                need_pagination = True
                break
        if need_pagination is False:
            return False
        url = self.make_url(offset=items['offset'] + items['limit'])
        self.pagination_next = url
        self.pagination_total = items['total']
        self.pagination_offset = items['offset']
        self.pagination_limit = items['limit']
        self.pagination_next_offset = items['offset'] + items['limit']
        return True

    '''
        Parameters
        A hash for storing script parameter, each node have a copy of them.
        TODO: each node don't need to copy parameter
    '''

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
        @param default=None: value set when parameter not found or value is None
        @param to='raw': string, converter used (raw is returning value unchanged)
        '''
        if self.parameters is None:
            return getattr(converter, to)(default)
        if name not in self.parameters:
            return getattr(converter, to)(default)
        value = self.parameters[name]
        if value is None:
            debug.warn(self, '{} value is None', name)
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
        item = xbmcgui.ListItem(
            ka['label'],
            ka['label2'],
            ka['image'],
            ka['image'],
            ka['url']
        )
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
                    return self.data[name][random.randrange(len(self.data[name]))]
        return self.get_property('image')

    def set_image(self, image):
        self.image = image
        return self

    def get_label2(self):
        return self.label2

    def render_nodes(self, nt, parameters, lvl=1, whiteFlag=Flag.ALL,
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

    def populating(self, Dir, lvl=1, whiteFlag=Flag.ALL, blackFlag=Flag.NONE,
                   data={}):
        if Dir.Progress.iscanceled():
            return False
        if lvl != -1 and lvl < 1:
            return False
        if not (self.nt & blackFlag == self.nt):
            new_data = self.fetch(Dir, lvl, whiteFlag, blackFlag)
            if new_data is None:
                return False
            else:
                data.update(new_data)
                self.data = data
                self.__add_pagination(self.data)
        self.populate(Dir, lvl, whiteFlag, blackFlag)
        if lvl != -1:
            lvl -= 1
        label = self.get_label()
        self.__add_pagination_node(Dir, lvl, whiteFlag)
        for child in self.childs:
            if Dir.is_canceled():
                return False
            if child.nt & whiteFlag == child.nt:
                if not Dir.add_node(child):
                    debug.error(self, "Could not add node")
                    raise exception.BuildCanceled('down')
            child.populating(Dir, lvl, whiteFlag, blackFlag)

    def populate(self, xbmc_directory=None, lvl=-1, whiteFlag=Flag.ALL,
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
            colorItem = getSetting('color_item')
            params = config.app.bootstrap.params
            params['offset'] = self.pagination_next_offset
            params['nid'] = self.nid
            node = getNode(self.nt, params)
            node.data = self.data
            node.label = u'{label} [{next_offset} / {pagination_total}]'.format(label=self.get_label(),
                                    next_offset=self.pagination_next_offset,
                                    pagination_total=self.pagination_total)
            node.label2 = u'[ {} / {} ]'.format(self.pagination_next_offset,
                                                self.pagination_total)
            self.add_child(node)

    def attach_context_menu(self, item, menu):
        '''Note: Url made with make_url must set mode (like mode=Mode.VIEW)
            else we are copying current mode (for track it's Mode.PLAY ...)
        '''
        ''' HOME '''
        colorCaution = getSetting('item_caution_color')

        url = self.make_url(nt=Flag.ROOT, mode=Mode.VIEW, nm='')
        menu.add(path='qobuz', label="Qobuz", cmd=containerUpdate(url, False),
                 id='', pos=-5)
        ''' ARTIST '''
        if self.nt & (Flag.ALBUM | Flag.TRACK | Flag.ARTIST):
            artist_id = self.get_artist_id()
            artist_name = self.get_artist()
            urlArtist = self.make_url(nt=Flag.ARTIST, nid=artist_id,
                                      mode=Mode.VIEW)
            menu.add(path='artist/all_album',
                          label="%s %s" % (lang(30157), artist_name),
                          cmd=containerUpdate(urlArtist), pos=-10)

            ''' Similar artist '''
            url = self.make_url(nt=Flag.SIMILAR_ARTIST,
                                nid=artist_id, mode=Mode.VIEW)
            menu.add(path='artist/similar',
                          label=lang(30160),
                          cmd=containerUpdate(url))
        ''' FAVORITES '''
        wf = self.nt & (~Flag.FAVORITE)
        if self.parent:
            wf = wf and self.parent.nt & ~Flag.FAVORITE
        if wf:
            ''' ADD TO FAVORITES / TRACKS'''
            url = self.make_url(nt=Flag.FAVORITE,
                                nm='', mode=Mode.VIEW)
            menu.add(path='favorites', label="Favorites",
                     cmd=containerUpdate(url, True), pos=-9)
            url = self.make_url(nt=Flag.FAVORITE,
                                nm='gui_add_tracks',
                                qid=self.nid,
                                qnt=self.nt,
                                mode=Mode.VIEW)
            menu.add(path='favorites/add_tracks',
                          label=lang(30167) + ' tracks', cmd=runPlugin(url))
            ''' ADD TO FAVORITES / Albums'''
            url = self.make_url(nt=Flag.FAVORITE,
                                nm='gui_add_albums',
                                qid=self.nid,
                                qnt=self.nt,
                                mode=Mode.VIEW)
            menu.add(path='favorites/add_albums',
                          label=lang(30167) + ' albums', cmd=runPlugin(url))
            ''' ADD TO FAVORITES / Artists'''
            url = self.make_url(nt=Flag.FAVORITE,
                                nm='gui_add_artists',
                                qid=self.nid,
                                qnt=self.nt,
                                mode=Mode.VIEW)
            menu.add(path='favorites/add_artists',
                          label=lang(30167) + ' artists', cmd=runPlugin(url))

        if self.parent and (self.parent.nt & Flag.FAVORITE):
            url = self.make_url(nt=Flag.FAVORITE,
                                nm='', mode=Mode.VIEW)
            menu.add(path='favorites', label="Favorites",
                     cmd=containerUpdate(url, True), pos=-9)
            url = self.make_url(nt=Flag.FAVORITE, nm='gui_remove',
                                qid=self.nid, qnt=self.nt,
                                mode=Mode.VIEW)
            menu.add(path='favorites/remove',
                     label='Remove %s' % (self.get_label()),
                     cmd=runPlugin(url), color=colorCaution)
        wf = ~Flag.USERPLAYLISTS
#        if self.parent:
#            wf = wf and self.parent.nt & (~Flag.USERPLAYLISTS)
        if wf:
            ''' PLAYLIST '''
            cmd = containerUpdate(self.make_url(nt=Flag.USERPLAYLISTS,
                                                nid='', mode=Mode.VIEW))
            menu.add(path='playlist', pos=1,
                          label="Playlist", cmd=cmd, mode=Mode.VIEW)

            ''' ADD TO CURRENT PLAYLIST '''
            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST,
                                          nm='gui_add_to_current',
                                          qnt=self.nt,
                                          mode=Mode.VIEW,
                                          qid=self.nid))
            menu.add(path='playlist/add_to_current',
                          label=lang(30161), cmd=cmd)
            label = self.get_label()
            try:
                label = label.encode('utf8', 'replace')
            except:
                debug.warn(self, "Cannot set query..." + repr(label))
                label = ''
            label = urllib.quote_plus(label)
            ''' ADD AS NEW '''
            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST,
                                          nm='gui_add_as_new',
                                          qnt=self.nt,
                                          query=label,
                                          mode=Mode.VIEW,
                                          qid=self.nid))
            menu.add(path='playlist/add_as_new',
                          label=lang(30082), cmd=cmd)

#            ''' Show playlist '''
#            if not (self.nt ^ Flag.USERPLAYLISTS != Flag.USERPLAYLISTS):
#                cmd = containerUpdate(self.make_url(nt=Flag.USERPLAYLISTS,
#                                    id='', mode=Mode.VIEW))
#                menu.add(path='playlist/show',
#                          label=lang(30162), cmd=cmd)

        ''' PLAYLIST / CREATE '''
        cFlag = (Flag.PLAYLIST | Flag.USERPLAYLISTS)
        if self.nt | cFlag == cFlag:
            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST,
                                          nm="gui_create", mode=Mode.VIEW))
            menu.add(path='playlist/create',
                          label=lang(30164), cmd=cmd)
        ''' VIEW BIG DIR '''
        cmd = containerUpdate(self.make_url(mode=Mode.VIEW_BIG_DIR))
        menu.add(path='qobuz/big_dir',
                 label=lang(30158), cmd=cmd)
        if getSetting('enable_scan_feature', asBool=True):
            ''' SCAN
            '''
            query = urllib.quote_plus(self.make_url(mode=Mode.SCAN,
                                                    asLocalUrl=True))
            url = self.make_url(nt=Flag.ROOT, mode=Mode.VIEW, nm='gui_scan',
                                query=query)
            menu.add(path='qobuz/scan', cmd=runPlugin(url), label='scan')
        if self.nt & (Flag.ALL & ~Flag.ALBUM & ~Flag.TRACK
                      & ~Flag.PLAYLIST):
            ''' ERASE CACHE
            '''
            cmd = runPlugin(self.make_url(nt=Flag.ROOT, nm="cache_remove",
                                          mode=Mode.VIEW))
            menu.add(path='qobuz/erase_cache',
                          label=lang(30117), cmd=cmd,
                          color=colorCaution, pos=10)
            ''' HTTP / Kooli
            '''
            cmd = runPlugin(self.make_url(nt=Flag.TESTING, nm="window_httpd",
                                          mode=Mode.VIEW))
            menu.add(path='qobuz/test httpd',
                          label='Test web service', cmd=cmd, pos=11)
            ''' Stop scan
            '''
            cmd = runPlugin(self.make_url(nt=Flag.ROOT, nm="stop_scan",
                                          mode=Mode.VIEW))
            menu.add(path='qobuz/stop_scan',
                          label='Stop scan', cmd=cmd, pos=12)

    def get_user_storage(self):
        if self.user_storage:
            return self.user_storage
        filename = os.path.join(cache.base_path,
                                'user-%s.local' % str(api.user_id))
        self.user_storage = _Storage(filename)
        return self.user_storage

    def get_user_path(self):
        return os.path.join(cache.base_path)

    def get_user_data(self):
        data = api.get('/user/login', username=api.username,
                       password=api.password)
        if not data:
            return None
        return data['user']

    def get_class_name(self):
        return self.__class__.__name__

    def as_dict(self):
        return {k: getattr(self, 'get_%s' % k)() for k in ['class_name', 'nid', 'parent']}

    def __str__(self):
        return '<{class_name} nid={nid}>'.format(**self.as_dict())

    def get_node_storage(self):
        if self.node_storage is not None:
            return self.node_storage
        path = os.path.join(cache.base_path, self._get_node_storage_filename())
        self.node_storage = _Storage(path)
        return self.node_storage

    def _get_node_storage_filename(self):
        raise NotImplmentedError()

    def remove_playlist_storage():
        path = os.path.join(cache.base_path, self._get_node_storage_filename())
        if os.path.exists(path):
            os.unlink(path)

    def get_image_from_storage(self):
        desired_size = getSetting('image_default_size', default=None)
        images = []
        if self.nid is not None:
            storage = self.get_node_storage()
            if storage is not None:
                images_len = 0
                if 'image' not in storage:
                    images = dataUtil.list_image(self.data, desired_size=desired_size)
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
                debug.error(self, 'Cannot get node storage')
        return None
