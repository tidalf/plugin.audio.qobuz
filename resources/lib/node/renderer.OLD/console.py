'''
    node.renderer.console
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from xbmcpy.console import console as con
from node import url2dict

class ItemFactory(object):

    def make_item(self, node):
        pass

from collections import deque

class ConsoleRenderer(deque):
    valid_commands = ['view', 'back']

    def __init__(self):
        self.makeItem = ItemFactory()
        self.alive = True
        self.stack_env = []
        self.plugin = None
        self.depth = 1
        self.whiteFlag = None

    def append(self, node):
        return super(ConsoleRenderer, self).append(node)

    def render(self, plugin, node):
        self.clear()
        self.plugin = plugin
        node.populating(self, self.depth, self.whiteFlag)
        self.end()

    def ask(self):
        cmd, args = self.get_command()
        try:
            return getattr(self, 'command_%s' % (cmd))(args)
        except Exception as e:
            con.write('Invalid command: %s\n' % (e))
        return False

    def get_command(self):
        inp = con.raw_input('#>')
        inpx = inp.split(' ')
        if inpx[0] not in self.valid_commands:
            return ('invalid', (inpx[0]))
        return (inpx[0], inpx[1:])

    def end(self):
        count = 0
        for node in iter(self):
            con.write('[%s] %s\n' % (count, str(node)))
            count+=1
        return True

    def command_view(self, args):
        if len(args) == 0:
            con.write('You must supply id: view <id>\n')
            return False
        idx = int(args[0])
        if idx is None:
            idx = 0
        node = self[idx]
        self.stack_env.insert(0, self.plugin._parameters.copy())
        self.plugin._parameters = url2dict(node.url())
        return True

    def command_back(self, args):
        self.plugin._parameters = self.stack_env.pop(0)
        return True

    def command_invalid(self, args):
        con.write('Invalid command: %s\n' % args[0])
