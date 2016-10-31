'''
    qobuz.node.text
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz.gui.util import lang, getImage
from qobuz.node import getNode, Flag


class Node_text(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_text, self).__init__(parent=parent,
                                               parameters=parameters,
                                               data=data)
        self.nt = Flag.TEXT
        self.label = self.get_parameter('label')
        self.label2 = self.get_parameter('label2')
        self.image = self.get_parameter('image')
        self.is_folder = False
        self.content_type = 'files'
