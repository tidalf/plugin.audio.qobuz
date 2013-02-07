from base import BaseRenderer

class ListRenderer(BaseRenderer):

    def __init__(self):
        self.alive = False
        self.depth = 1
        self.whiteFlag = None
        self.blackFlag = None

    def render(self, plugin, node):
        self.clear()
        node.populating(self, self.depth, self.whiteFlag)
        self.end()

    def ask(self):
        pass

    def end(self):
        print "Count %s" % (len(self))
