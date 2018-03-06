'''
    qobuz.node.text
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.gui.util import getImage
from qobuz.node import Flag
from qobuz.node.inode import INode


class Node_text(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_text, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.TEXT
        self.label = self.get_parameter('label')
        self.label2 = self.get_parameter('label2')
        self.image = self.get_parameter('image')
        self.is_folder = False
        self.content_type = 'files'
