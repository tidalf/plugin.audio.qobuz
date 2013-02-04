from collections import deque

class ListRenderer(deque):

    def __init__(self):
        self.alive = False
        self.depth = -1
        self.whiteFlag = None
#        
#    def append(self, node):
#        return super(ListRenderer, self).append(node)

    def render(self, plugin, node):
        self.clear()
        node.populating(self, self.depth, self.whiteFlag)
        self.end()

    def ask(self):
        pass

    def end(self):
        print "Count %s" % (len(self))
