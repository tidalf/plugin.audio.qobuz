'''
    qobuz.node.artist
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.contextmenu import contextMenu
from qobuz.gui.util import getImage
from qobuz.api import api
from qobuz.node import getNode, Flag

def helper_album_list_genre(data, default=[]):
    if 'albums' not in data:
        return default
    genres = {}
    for album in data['albums']['items']:
        if 'genre' not in album:
            continue
        genres[album['genre']['name']] = 1
    return genres.keys()


class Node_artist(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_artist, self).__init__(parent=parent,
                                          parameters=parameters,
                                          data=data)
        self.nt = Flag.ARTIST
        self.set_label(self.get_name())
        self.content_type = 'artists'

    def hook_post_data(self):
        self.nid = self.get_parameter('nid', default=None) or \
            self.get_property('id', default=None)
        self.name = self.get_property('name')
        self.image = self.get_image()
        self.label = self.name

    def fetch(self, *a, **ka):
        return api.get('/artist/get', artist_id=self.nid, extra='albums')

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        if 'albums' not in self.data:
            return False
        self.content_type = 'albums'
        for data in self.data['albums']['items']:
            album = getNode(Flag.ALBUM, data=data)
            cache = album.fetch(noRemote=True)
            if cache is not None:
                album.data = cache
            self.add_child(album)
        return True if len(self.data['albums']['items']) > 0 else False

    def get_artist_id(self):
        return self.nid

    def get_image(self):
        return self.get_property(['image/extralarge',
                                   'image/mega',
                                   'image/large',
                                   'image/medium',
                                   'image/small',
                                   'picture'], default=getImage('artist'))

    def get_label(self, fmt='%a (%C)'):
        fmt = fmt.replace('%a', self.get_artist())
        fmt = fmt.replace('%G', self.get_genre())
        fmt = fmt.replace('%C', str(self.get_property('albums_count',
                                                      default=0)))
        return fmt

    def get_title(self):
        return self.get_name()

    def get_artist(self):
        return self.get_name()

    def get_name(self):
        return self.get_property('name')

    def get_genre(self):
        return ', '.join(helper_album_list_genre(self.data))

    def get_owner(self):
        return self.get_property('owner/name')

    def get_description(self):
        return self.get_property('biography/content', to='strip_html')

    def makeListItem(self, replaceItems=False):
        genre = self.get_genre()
        import xbmcgui
        item = xbmcgui.ListItem(self.get_label(),
                                self.get_label(),
                                self.get_image(),
                                self.get_image(),
                                self.make_url())
        if not item:
            debug.warn(self, 'Error: Cannot make xbmc list item')
            return None
        item.setPath(self.make_url())
        item.setInfo('Music', infoLabels={
            'artist': self.get_artist(),
            'genre': genre
        })
        item.setProperty('artist_genre', genre)
        item.setProperty('artist_description', self.get_description())
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item
