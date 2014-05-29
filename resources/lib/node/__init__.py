'''
    node
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
__all__ = ['Mode', 'Flag', 'url2dict', 'dict2url']

import pprint
import collections
import copy

from urllib import quote, unquote


class BaseFlag(object):
    Base = 1 << 0

Flag = BaseFlag()

__base_properties__ = {
    'nid': 0,
    'kind': Flag.Base
}


class _Mode_():

    def __init__(self):
        self.VIEW = 1 << 1
        self.PLAY = 1 << 2
        self.SCAN = 1 << 3
        self.VIEW_BIG_DIR = 1 << 4

    def to_s(self, mode):
        if mode == self.VIEW:
            return "view"
        elif mode == self.PLAY:
            return "play"
        elif mode == self.SCAN:
            return "scan"
        elif mode == self.VIEW_BIG_DIR:
            return "view big dir"
        else:
            raise Exception("Unknow mode: %s" % (str(mode)))

Mode = _Mode_()


def url2dict(url):
    '''Convert url query parameter (?foo=bar&fi=fu) to python dictionary
    '''
    if url.startswith('?'):
        url = url[1:]
    urlx = url.split('&')
    d = {}
    for kv in urlx:
        kvx = kv.split('=')
        d[kvx[0]] = kvx[1]
    return d


def dict2url(d):
    '''Convert dictionary to url query parameter
    '''
    url = ''
    for k in d:
        url += '%s=%s&' % (k, d[k])  # urllib.quote_plus(d[k]))
    return url[:-1]


class Commander(object):

    def __init__(self, flag, getNode):
        self.flag = flag
        self.getNode = getNode

    def has_action(self, node):
        if node.get_parameter('action'):
            return True
        return False

    def execute(self, renderer, node):
        action = node.get_parameter('action', delete=True)
        if not action:
            return True
        tkind = node.get_parameter('target', delete=True)
        target = None
        if tkind:
            tmp = node
            node = self.getNode(tkind, node.parameters)
            target = tmp
        nodename = self.flag.to_s(node.kind)
        return getattr(self, '%s_%s' % (nodename, action))(renderer, node,
                                                           target)


class BaseNode(collections.deque):
    '''Our base node that act like a list for his childs
    '''
    def __init__(self, parameters={}):
        self.parameters = parameters.copy()
        self.nid = self.get_property('id') or self.get_parameter('nid')
        self.parent = None
        self.is_folder = True
        self.is_playable = False
        self.label = None
        self.label2 = None
        self.image = None
        self.data = None
        self.mode = Mode.VIEW
        self.actions = {}
        super(BaseNode, self).__init__(self)

    def pretty(self, Flag):
        s = '[ %s ]\n' % (Flag.to_s(self.kind))
        s += ' ::nid:\t%s\n' % self.nid
        s += ' ::label:\t%s\n' % self.label
        for p in ['kind', 'mode', 'parent', 'is_folder',
                  'image']:
                s += ' ::%s\t%s\n' % (p, self.__dict__[p])
        s += ' ::IsPlayable: %s\n' % (self.is_playable)
        s += ' ::Parameters\n\t%s\n' % self.parameters
        s += ' ::Actions\n'
        for a in self.actions:
            kind = self.kind
            if 'target' in self.actions[a]:
                kind = self.actions[a]['target']
            s += ' [ %s ]\t%s (%s)\n' % (Flag.to_s(kind), a,
                                         self.actions[a]['label'])
        return s

    def add_action(self, path, **ka):
        self.actions[path] = ka

    def exec_action(self, *a, **ka):
        action = self.get_parameter('action', delete=True)
        if not action:
            return True
        action = action.replace('/', '_')
        methodname = 'action_%s' % (action)
        return getattr(self, methodname)(*a, **ka)

    def has_action(self):
        return self.get_parameter('action')

    def append(self, node):
        node.parent = self
        return super(BaseNode, self).append(node)

    def set_parameter(self, path, value, **ka):
        if 'encode' in ka and ka['encode']:
            value = quote(value)
        elif 'isBool' in ka and ka['isBool']:
            value = True if value else False
        self.parameters[path] = value

    def get_parameter(self, path, **ka):
        if not path in self.parameters:
            return None
        value = self.parameters[path]
        if 'delete' in ka and ka['delete']:
            del self.parameters[path]
        if value is None:
            return None
        if 'decode' in ka and ka['decode']:
            value = unquote(value)
        if 'number' in ka and ka['number']:
            value = int(value)
        return value

    def url(self, **ka):
        for label in ['kind', 'mode', 'nid']:
            if not label in ka:
                v = getattr(self, label)
                if v is not None:
                    ka[label] = v
        return '?%s' % (dict2url(ka))

    def fetch(self, renderer):
        return True

    def populate(self, renderer):
        return True

    def populating(self, renderer):
#        print "POPULATING .... %s %s" % (str(depth), str(self))
        if renderer.depth == 0:
            return False
        if renderer.depth != -1:
            if renderer.depth <= 0:
                renderer.depth = 0
                return False
        if self.kind & renderer.blackFlag != self.kind:
            if not self.fetch(renderer):
                return False
            if not self.populate(renderer):
                return True
        if renderer.depth != -1:
            renderer.depth -= 1
        if len(self) == 0:
            return True
        if hasattr(self, 'populating_hook_before_traversal'):
            self.populating_hook_before_traversal(renderer)
        for child in self:
            if child.kind & renderer.whiteFlag == child.kind:
                renderer.append(child)
            else:
                print u"Rejecting node: %s" % child.get_label().encode('ascii',
                                                                    'replace')
            child.populating(renderer)
        if hasattr(self, 'populating_hook_after_traversal'):
            self.populating_hook_after_traversal(renderer)
        return True

    '''Getters
    '''
    def get_label(self):
        return self.label or __name__

    def get_image(self):
        return self.image or ''

    '''Property'''
    def get_property(self, pathList):
        """Property are just a easy way to access JSON data (self.data)
            Parameters:
            pathList: a string or a list of string, each string can be
                a path like 'album/image/large'
            Return:
                string (empty string when all fail or when there's no data)
            * When passing array of string the method return the first
            path returning data

            Example:
                image = self.get_property(['image/extralarge',
                                       'image/mega',
                                       'picture'])
        """
        if isinstance(pathList, basestring):
            return self.__get_property(pathList)
        for path in pathList:
            data = self.__get_property(path)
            if data:
                return data
        return ''

    def __get_property(self, path):
        """Helper used by get_property method
        """
        if not self.data:
            return ''
        xPath = path.split('/')
        root = self.data
        for i in range(0, len(xPath)):
            if not xPath[i] in root:
                return ''
            root = root[xPath[i]]
        if root and root != 'None':
            return root
        return ''

    ''' nid (Node Id)'''
    @property
    def nid(self):
        return self._nid

    @nid.setter
    def nid(self, value):
        self._nid = value

    @nid.getter
    def nid(self):
        if self.data and 'id' in self.data:
            return self.data['id']
        return self._nid

    def __str__(self):
        s = u'%8s % 20s (%s)' % (self.kind, repr(self.get_label()), self.url())
        return s
