'''
    qobuz.node.inode.main
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys
import urllib
import random

from .context_menu import attach_context_menu
from .pagination import add_pagination
from .props import node_type_from_class, node_image_from_class, node_contenttype_from_class
from qobuz import config
from qobuz import exception
from qobuz.api import api
from qobuz.api.user import current as current_user
from qobuz.cache import cache
from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.gui.contextmenu import contextMenu
from qobuz.gui.util import runPlugin, containerUpdate
from qobuz.node import Flag, getNode
from qobuz.renderer import renderer
from qobuz.storage import _Storage
from qobuz.theme import color
from qobuz.util import data as dataUtil
from qobuz.util import properties
from qobuz.util.converter import converter

logger = getLogger(__name__)


def get_property_helper(data, path, to):
    try:
        _path, value = properties.deep_get(data, path)
    except KeyError:
        return None
    if value is None:
        return None
    return getattr(converter, to)(value)


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

    def __init__(self, parent=None, parameters=None, data=None):
        '''Constructor
        @param parent=None: Parent node if not None
        @param parameters={}: dictionary
        '''
        self._content_type = None
        self._data = None
        self._label = None
        self._nid = None
        self._parent = None

        self.data = data
        self.parameters = {} if parameters is None else parameters
        self.parent = parent

        self.content_type = node_contenttype_from_class(
            self.__class__) or 'files'
        self.image = node_image_from_class(self.__class__)
        self.nt = node_type_from_class(self.__class__)

        self.childs = []
        self.hasWidget = False
        self.is_folder = True
        self.label = None
        self.label2 = None
        self.limit = config.app.registry.get('pagination_limit', to='int')
        self.mode = self.get_parameter('mode', to='int')
        self.nid = self.get_parameter(
            'nid', default=None) or self.get_property('id', default=None)
        self.node_storage = None
        self.offset = self.get_parameter('offset', default=0)
        self.pagination_next = None
        self.pagination_prev = None
        self.user_storage = None
        self.user_storage = None

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
        if self.data is None:
            return default
        if isinstance(pathList, basestring):
            pathList = [pathList]
        for path in pathList:
            value = get_property_helper(self.data, path, to)
            if value is not None:
                return value
        return default

    def __getattr__(self, attr):
        if attr.startswith('get_') and hasattr(self, 'propsMap'):
            key = attr[4:]
            if key in self.propsMap:
                prop = self.propsMap.get(key)
                default = prop.get('default') if hasattr(
                    prop, 'default') else None
                if self.data is None:
                    return lambda *a, **ka: default
                try:
                    _path, value = properties.get_mapped(
                        self.data,
                        self.propsMap,
                        key,
                        default=default)
                    return lambda *a, **ka: value
                except KeyError:
                    pass
        raise AttributeError(attr)

    def __add_pagination(self, data):
        return add_pagination(self, data)

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
        from kodi_six import xbmcgui  # pylint:disable=E0401
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

    @classmethod
    def render_nodes(cls,
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

    def fetch(self, xdir=None, lvl=1, whiteFlag=None, blackFlag=None,
              noRemote=False):
        '''When returning None we are not displaying directory content
        '''
        return {}

    def populating(self, xdir,
                   lvl=1,
                   whiteFlag=Flag.ALL,
                   blackFlag=Flag.NONE,
                   data=None):
        data = {} if data is None else data
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
                 xdir=None,
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
        return attach_context_menu(self, item, menu)

    def get_user_storage(self):
        if self.user_storage is not None:
            return self.user_storage
        filename = os.path.join(cache.base_path,
                                'user-%s.local' % str(current_user.get_id()))
        self.user_storage = _Storage(filename)
        return self.user_storage

    @classmethod
    def get_user_path(cls):
        return os.path.join(cache.base_path)

    @classmethod
    def get_user_data(cls):
        data = api.get('/user/login',
                       username=current_user.username,
                       password=current_user.password)
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
        raise NotImplementedError(self)

    def remove_playlist_storage(self):
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
