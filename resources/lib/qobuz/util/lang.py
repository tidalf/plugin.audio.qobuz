'''
    qobuz.lang
    ~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import xml.etree.ElementTree as ET


class Lang(object):

    def __init__(self, name):
        self.seen = {}
        if name is None:
            name = 'english'
        name = name.capitalize()
        self.name = name
        self.path_langs = os.path.abspath(
                                        os.path.join(os.path.dirname(__file__),
                                        os.path.pardir, os.path.pardir,
                                        os.pardir, 'language'))

        path = os.path.abspath(os.path.join(self.path_langs,
                                            name.capitalize()))
        if not os.path.exists(path):
            raise ValueError('Invalid language: %s' % name)
        self.path = path
        if not self.parse():
            raise ValueError('Could not parse xml file %s', path)

    def parse(self, name=None):
        self.root = None
        if name is None:
            name = self.name
        path = os.path.join(self.path_langs, name, 'strings.xml')
        self.root = ET.parse(os.path.join(path))
        return self.root

    def lang(self, lid):
        lid = int(lid)
        if lid in self.seen:
            return self.seen[lid]

if __name__ == '__main__':
    uk = Lang('english')
    uk.parse()
