'''
    qobuz.renderer.irenderer
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node import Flag
from qobuz.node import getNode


class IRenderer(object):
    '''Base class for our renderer
        Parameters:
        node_type: int, type of node (see node.NodeFlag)
        parameters: dictionary, parameters passed to our plugin
    '''

    def __init__(self,
                 node_type,
                 parameters=None,
                 mode=None,
                 whiteFlag=Flag.ALL,
                 blackFlag=Flag.STOPBUILD,
                 depth=1,
                 asList=False):
        self.node_type = node_type
        self.parameters = {} if parameters is None else parameters
        self.root = None
        self.whiteFlag = whiteFlag
        self.blackFlag = blackFlag
        self.depth = depth
        self.asList = asList
        self.nodes = []
        self.mode = mode

    def set_root_node(self):
        '''Import correct node object based on node_type parameter, setting
        self.root
        '''
        if self.root:
            return self.root
        self.root = getNode(self.node_type, self.parameters)
        return self.root

    def has_method_parameter(self):
        '''Return true if our plugin has been called with a node method
        parameter (nm=foo)
        '''
        if 'nm' in self.parameters:
            return True
        return False

    def execute_method_parameter(self):
        '''Excute node method (nm=foo) if present and delete nm key
        from parameter
        '''
        if 'nm' in self.parameters:
            methodName = self.parameters['nm']
            del self.parameters['nm']
            if getattr(self.root, methodName)():
                return True
            return False

    def run(self):
        raise NotImplementedError()
