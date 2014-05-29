'''
    qobuz.node.favorite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from inode import INode
from qobuz.debug import warn
from qobuz.node import getNode, Flag
from qobuz.api import api
from qobuz.i8n import _
from qobuz.cache import cache
from node.renderer.list import ListRenderer

'''Used to trigger po parser
'''
_('albums')
_('tracks')
_('artists')


class Node_favorite(INode):
    '''Displaying user favorites (track and album)
    '''
    def __init__(self, parameters={}):
        super(Node_favorite, self).__init__(parameters)
        self.kind = Flag.FAVORITE
        self.label = _('Favorites')
        self.content_type = 'albums'
        self.items_path = self.get_parameter('items_path', delete=True)
        if not self.items_path:
            self.items_path = 'albums'

    def get_label(self):
        return '%s / %s ' % (self.label, _(self.items_path))

    def url(self, **ka):
        if not 'items_path' in ka:
            ka['items_path'] = self.items_path
        return super(Node_favorite, self).url(**ka)

    def fetch(self, renderer=None):
        print "FETCH FAVORITE %s" % self.items_path
        data = api.get('/favorite/getUserFavorites',
                           user_id=api.user_id,
                           limit=api.pagination_limit,
                           offset=self.offset, type=self.items_path)
        if not data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        return getattr(self, '_populate_%s' % (self.items_path))(renderer)

    def _populate_tracks(self, renderer):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, self.parameters)
            node.data = track
            node.add_action('delete_track',
                            label=_('Remove track from favorite'),
                            target=self.kind)
            node.add_action('delete_tracks_from_album',
                            label=_('Remove all album tracks'),
                            target=self.kind)
            self.append(node)
        return True

    def _populate_albums(self, renderer):
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, self.parameters)
            node.data = album
            node.add_action('delete_album',
                            label=_('Remove album from favorite'),
                            target=self.kind)
            self.append(node)
        return True

    def _populate_artists(self, renderer):
        for artist in self.data['artists']['items']:
            node = getNode(Flag.ARTIST, self.parameters)
            node.data = artist
            node.add_action('delete_artist',
                            label=_('Remove artist from favorite'),
                            target=self.kind)
            self.append(node)
        return True

    def get_description(self):
        return self.get_property('description')

    def add_albums(self, album_ids):
        ret = api.favorite_create(album_ids=album_ids)
        if not ret:
            return False
        self.delete_cache('albums')
        return True

    def list_albums(self, target):
        album_ids = {}
        albums = []
        if target.kind & Flag.ALBUM == Flag.ALBUM:
            target.fetch()
            album_ids[str(target.nid)] = 1
            albums.append(target)
        elif target.kind & Flag.TRACK == Flag.TRACK:
            target.fetch()
            album = getNode(Flag.ALBUM, {})
            album.data = target.get_property('album')
            albums.append(album)
#            render = ListRenderer()
#            render.depth = 1
#            render.whiteFlag = Flag.TRACK
#            render.blackFlag = Flag.TRACK
#            render.render(target)
#            if len(render) > 0:
#                album = getNode(Flag.ALBUM, {})
#                album.data = render[0].data['album']
#                album_ids[str(album.nid)] = 1
#                albums.append(album)
        else:
            render = ListRenderer()
            render.depth = -1
            render.whiteFlag = Flag.ALBUM | Flag.TRACK
            render.blackFlag = Flag.TRACK
            render.render(target)
            for node in render:
                if node.kind & Flag.ALBUM == Flag.ALBUM:
                    if not str(node.nid) in album_ids:
                        album_ids[str(node.nid)] = 1
                        albums.append(node)
                if node.kind & Flag.TRACK == Flag.TRACK:
                    album = getNode(Flag.ALBUM,
                                    {'nid': node.get_property('album/id')})
                    if 'album' in node.data:
                        album.data = node.data['album']
                    else:
                        import pprint
                        print pprint.pformat(node.data)
                    if not str(album.nid) in album_ids:
                            albums.append(album)
                            album_ids[str(album.nid)] = 1
        return albums

    def add_artists(self, artist_ids):
        ret = api.favorite_create(artist_ids=artist_ids)
        if not ret:
            return False
        self.delete_cache('artists')
        return True

    def list_artists(self, target):
        artist_ids = {}
        artists = []
#        if target.kind & Flag.ARTIST == Flag.ARTIST:
#            target.fetch()
#            artist_ids[str(target.nid)] = 1
#            artists.append(target)
        if target.kind & Flag.TRACK == Flag.TRACK:
            if target.data is None:
                target.fetch()
            aid = target.get_artist_id()
            if aid is None:
                return artists
            artist = getNode(Flag.ARTIST, {'nid': aid})
            artist.data = {'nid': aid, 'name': target.get_artist()}
            artists.append(artist)
        else:
            render = ListRenderer()
            render.depth = -1
            render.whiteFlag = Flag.ALBUM | Flag.TRACK | Flag.ARTIST
            render.blackFlag = Flag.TRACK
            render.render(target)
            for node in render:
                aid = node.get_artist_id()
                if aid is None:
                    continue
                artist = getNode(Flag.ARTIST, {'nid': aid})
                if node.kind & Flag.ARTIST:
                    artist.data = node.data
                elif node.kind & Flag.ALBUM:
                    artist.data = node.data['artist']
                elif node.kind & Flag.TRACK:
                    artist.data = {'nid': aid, 'name': node.get_artist()}
                else:
                    artist.fetch()
                if not str(artist.nid) in artist_ids:
                    artists.append(artist)
                    artist_ids[str(artist.nid)] = 1
        return artists

    def add_tracks(self, track_ids):
        ret = api.favorite_create(track_ids=track_ids)
        if not ret:
            return False
        self.delete_cache('tracks')
        return True

    def list_tracks(self, root):
        track_ids = {}
        nodes = []
        if root.kind & Flag.TRACK == Flag.TRACK:
            root.fetch()
            track_ids[str(root.nid)] = 1
            nodes.append(root)
        else:
            render = ListRenderer()
            render.alive = False
            render.depth = -1
            render.whiteFlag = Flag.TRACK
            render.blackFlag = Flag.TRACK
            render.render(root)
            for node in render:
                if not str(node.nid) in track_ids:
                    nodes.append(node)
                    track_ids[str(node.nid)] = 1
        return nodes

    def delete_track(self, track_id):
        if api.favorite_delete(track_ids=track_id):
            self.delete_cache('tracks')
            return True
        return False

    def list_tracks_from_album(self, album_id):
        lr = ListRenderer()
        lr.whiteFlag = Flag.TRACK
        lr.blackFlag = Flag.TRACK
        lr.depth = 1
        self.populating(lr)
        tracks = []
        for track in lr:
            if track.get_album_id() == album_id:
                tracks.append(track)
        return tracks

    def delete_album(self, album_id):
        if api.favorite_delete(album_ids=album_id):
            self.delete_cache('albums')
            return True
        return False

    def delete_artist(self, artist_id):
        if api.favorite_delete(artist_ids=artist_id):
            self.delete_cache('artists')
            return True
        return False

    def delete_cache(self, ftype):
        key = cache.make_key('/favorite/getUserFavorites',
                           user_id=api.user_id,
                           limit=api.pagination_limit,
                           type=ftype,
                           offset=self.offset)
        return cache.delete(key)
