__all__ = ['BaseFlag', 'BaseNode', 'dict2url', 'url2dict' 'BaseMode']

import pprint
import collections
import copy

import urllib

class BaseFlag(object):
    Base = 1 << 0

Flag = BaseFlag()

__base_properties__ = {
    'nid': 0,
    'kind': Flag.Base
}

class BaseMode(object):
    VIEW = 1 << 1
    RVIEW = 1 << 2
    PLAY = 1 << 3
    SCAN = 1 << 4

Mode = BaseMode()

def url2dict(url):
    '''Convert url query parameter (?foo=bar&fi=fu) to python dictionary
    '''
    if url.startswith('?'):
        url = url[1:]
    urlx = url.split('&')
    d = {}
    for kv in urlx:
        kvx = kv.split('=')
        d[kvx[0]]= kvx[1]
    return d

def dict2url(d):
    '''Convert dictionary to url query parameter
    '''
    url = ''
    for k in d:
        url += '%s=%s&' % (k, d[k])#urllib.quote_plus(d[k]))
    return url[:-1]

class BaseNode(collections.deque):
    '''Our base node that act like a list for his childs
    '''
    def __init__(self, parameters={}):
        self.parameters = parameters.copy()
        self.nid = self.get_property('id') or self.get_parameter('nid')
        self.is_folder = True
        self.is_playable = False
        self.label = None
        self.label2 = None
        self.image = None
        self.data = None
        super(BaseNode, self).__init__(self)

    def append(self, node):
        node.parent = self
        return super(BaseNode, self).append(node)

    def set_parameter(self, path, value):
        self.parameters[path] = value

    def get_parameter(self, path):
        if not path in self.parameters:
            return None
        return self.parameters[path]

    def url(self, mode=Mode.VIEW):
        d = {'kind': self.kind, 'mode': mode}
        if self.nid:
            d['nid'] = self.nid
        return '?%s' % (dict2url(d))
    
    def fetch(self):
        return True

    def populate(self):
        return True

    def populating(self, directory, depth=1, whiteFlag=None, blackFlag=None):
        if depth != -1:
            if depth <= 0:
                depth = 0
                return False
        if not self.fetch():
            return False
        self.populate()
        if depth != -1:
            depth -= 1
        for child in iter(self):
            if child.kind & whiteFlag:
                directory.append(child)
            else:
                print "Rejecting node: %s" % (child)
            child.populating(directory, depth, whiteFlag, blackFlag)
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
