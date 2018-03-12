'''
    qobuz.node.favorite
    ~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from kodi_six import xbmcgui  # pylint:disable=E0401

from qobuz import exception
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.cache import cache
from qobuz.debug import getLogger
from qobuz.gui.util import getImage, notifyH, executeBuiltin, containerUpdate
from qobuz.gui.util import lang
from qobuz.node import getNode, Flag, helper
from qobuz.node.inode import INode
from qobuz.renderer import renderer

logger = getLogger(__name__)
dialogHeading = lang(30083)
all_kinds = ['albums', 'tracks', 'artists']


class Node_favorite(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_favorite, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self.nt = Flag.FAVORITE
        self.image = getImage('favorites')
        self.method = self.get_parameter('nm')
        self.search_type = self.get_parameter('search-type')
        self.content_type = 'songs'

    def get_label(self, default=None):
        if self.label is not None:
            return self.label
        if self.search_type is None:
            return lang(30081)
        elif self.search_type == 'all':
            return lang(30098)
        return self.search_type.capitalize()

    def fetch(self, options=None):
        if self.search_type is None:
            return {}
        if self.search_type != 'all':
            return api.get('/favorite/getUserFavorites',
                           user_id=user.get_id(),
                           type=self.search_type,
                           limit=self.limit,
                           offset=self.offset)
        return api.get('/favorite/getUserFavorites',
                       user_id=user.get_id(),
                       limit=self.limit,
                       offset=self.offset)

    def make_url(self, **ka):
        if self.search_type is not None:
            ka['search-type'] = self.search_type
        return super(Node_favorite, self).make_url(**ka)

    def populate(self, options=None):
        if self.method is not None:
            return True
        if self.search_type is None:
            for kind in all_kinds:
                self.add_child(
                    getNode(
                        Flag.FAVORITE, parameters={'search-type': kind}))
            self.add_child(
                getNode(
                    Flag.FAVORITE, parameters={'search-type': 'all'}))
            return True
        result = False
        search_for = (self.search_type, )
        if self.search_type == 'all':
            search_for = all_kinds
        for kind in search_for:
            if kind not in self.data:
                continue
            method = '_populate_%s' % kind
            if not hasattr(self, method):
                logger.warn('No method named %s', method)
                continue
            if getattr(self, method)(options):
                result = True
        return result

    def _populate_tracks(self, options):
        self.content_type = 'songs'
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, data=track)
            if not node.get_displayable():
                logger.warn(
                    'Track not displayable: %s (%s)',
                    node.get_label().encode(
                        'ascii', errors='ignore'),
                    node.nid)
                continue
            self.add_child(node)
        return True if len(self.data['tracks']['items']) > 0 else False

    def _populate_albums(self, options):
        self.content_type = 'albums'
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, data=album)
            if not node.get_displayable():
                logger.warn(
                    'Album not displayable: %s (%s)',
                    node.get_label().encode(
                        'ascii', errors='ignore'),
                    node.nid)
                continue
            cache = node.fetch(helper.TreeTraverseOpts(noRemote=True))
            if cache is not None:
                node.data = cache
            self.add_child(node)
        return True if len(self.data['albums']['items']) > 0 else False

    def _populate_artists(self, options):
        self.content_type = 'artists'
        for artist in self.data['artists']['items']:
            node = getNode(Flag.ARTIST, data=artist)
            node.data = node.fetch(helper.TreeTraverseOpts(noRemote=True))
            self.add_child(node)
        return True if len(self.data['artists']['items']) > 0 else False

    def get_description(self):
        return self.get_property('description', to='strip_html')

    def gui_add_albums(self):
        qnt, qid = int(self.get_parameter('qnt')), self.get_parameter('qid')
        nodes = self.list_albums(qnt, qid)
        if len(nodes) == 0:
            notifyH(dialogHeading, lang(30143))
            return False
        ret = xbmcgui.Dialog().select(
            lang(30144), [node.get_label() for node in nodes])
        if ret == -1:
            return False
        album_ids = ','.join([node.nid for node in nodes])
        if not self.add_albums(album_ids):
            notifyH(dialogHeading, 'Cannot add album(s) to favorite')
            return False
        self._delete_cache()
        notifyH(dialogHeading, 'Album(s) added to favorite')
        return True

    def gui_add_artists(self):
        qnt, qid = int(self.get_parameter('qnt')), self.get_parameter('qid')
        nodes = self.list_artists(qnt, qid)
        if not nodes:
            notifyH(dialogHeading, lang(30143))
            return False
        ret = xbmcgui.Dialog().select(
            lang(30146), [node.get_label() for node in nodes])
        if ret == -1:
            return False
        artist_ids = ','.join([str(node.nid) for node in nodes])
        if not self.add_artists(artist_ids):
            notifyH(dialogHeading, 'Cannot add artist(s) to favorite')
            return False
        self._delete_cache()
        notifyH(dialogHeading, 'Artist(s) added to favorite')
        return True

    def list_albums(self, qnt, qid):
        ''' List albums givent a node type and a node id
        '''
        album_ids = {}
        nodes = []
        if qnt & Flag.ALBUM == Flag.ALBUM:
            node = getNode(Flag.ALBUM, {'nid': qid})
            node.data = node.fetch()
            album_ids[str(node.nid)] = 1
            nodes.append(node)
        elif qnt & Flag.TRACK == Flag.TRACK:
            render = renderer(qnt, self.parameters)
            render.depth = 1
            render.whiteFlag = Flag.TRACK
            render.blackFlag = Flag.NONE
            render.asList = True
            render.run()
            if not render.nodes:
                node = getNode(Flag.ALBUM)
                node.data = render.nodes[0].data['album']
                album_ids[str(node.nid)] = 1
                nodes.append(node)
        else:
            render = renderer(qnt, self.parameters)
            render.depth = -1
            render.whiteFlag = Flag.ALBUM
            render.blackFlag = Flag.STOPBUILD & Flag.TRACK
            render.asList = True
            render.run()
            for node in render.nodes:
                if node.nt & Flag.ALBUM and str(node.nid) not in album_ids:
                    album_ids[str(node.nid)] = 1
                    nodes.append(node)
                if node.nt & Flag.TRACK:
                    render = renderer(qnt, self.parameters)
                    render.depth = 1
                    render.whiteFlag = Flag.TRACK
                    render.blackFlag = Flag.NONE
                    render.asList = True
                    render.run()
                    if not render.nodes:
                        newnode = getNode(
                            Flag.ALBUM, data=render.nodes[0].data['album'])
                        if not str(newnode.nid) in album_ids:
                            nodes.append(newnode)
                            album_ids[str(newnode.nid)] = 1
        return nodes

    def add_albums(self, album_ids):
        ret = api.favorite_create(album_ids=album_ids)
        if not ret:
            return False
        self._delete_cache()
        return True

    def add_artists(self, artist_ids):
        ret = api.favorite_create(artist_ids=artist_ids)
        if not ret:
            return False
        self._delete_cache()
        return True

    def gui_add_tracks(self):
        qnt, qid = int(self.get_parameter('qnt')), self.get_parameter('qid')
        nodes = self.list_tracks(qnt, qid)
        if len(nodes) == 0:
            notifyH(dialogHeading, lang(3600))
            return False
        label = lang(30145)
        from qobuz.gui.dialog import DialogSelect
        for node in nodes:
            try:
                label = node.get_label()
                if label is not None:
                    label = label.encode('utf8', errors='ignore')
            except Exception as e:
                logger.error(u'Error: %s', e)
        dialog = DialogSelect(
            label=label, items=[node.get_label() for node in nodes])
        if dialog.open() == -1:
            return False
        track_ids = ','.join([str(node.nid) for node in nodes])
        if not self.add_tracks(track_ids):
            notifyH(dialogHeading, 'Cannot add track(s) to favorite')
            return False
        self._delete_cache()
        notifyH(dialogHeading, 'Track(s) added to favorite')
        return True

    def list_tracks(self, qnt, qid):
        '''List tracks given a node type and a node id
        '''
        track_ids = {}
        nodes = []
        if qnt & Flag.TRACK == Flag.TRACK:
            node = getNode(Flag.TRACK, parameters={'nid': qid})
            node.data = node.fetch()
            track_ids[str(node.nid)] = 1
            nodes.append(node)
        else:
            render = renderer(qnt, self.parameters)
            render.depth = -1
            render.whiteFlag = Flag.TRACK
            render.asList = True
            render.run()
            for node in render.nodes:
                if str(node.nid) not in track_ids:
                    nodes.append(node)
                    track_ids[str(node.nid)] = 1
        return nodes

    def list_artists(self, qnt, qid):
        artist_ids = {}
        nodes = []
        if qnt & Flag.ARTIST == Flag.ARTIST:
            node = getNode(Flag.ARTIST, {'nid': qid})
            node.fetch(None, None, None, Flag.NONE)
            artist_ids[str(node.nid)] = 1
            nodes.append(node)
        else:
            render = renderer(qnt, self.parameters)
            render.depth = -1
            render.whiteFlag = Flag.ALBUM & Flag.TRACK
            render.blackFlag = Flag.TRACK & Flag.STOPBUILD
            render.asList = True
            render.run()
            for node in render.nodes:
                artist = getNode(Flag.ARTIST, {'nid': node.get_artist_id()})
                if not artist.fetch(None, None, None, Flag.NONE):
                    continue
                if not str(artist.nid) in artist_ids:
                    nodes.append(artist)
                    artist_ids[str(artist.nid)] = 1
        return nodes

    def add_tracks(self, track_ids):
        ret = api.favorite_create(track_ids=track_ids)
        if not ret:
            return False
        self._delete_cache()
        return True

    def _delete_cache(self):
        keys = [cache.make_key(
            '/favorite/getUserFavorites',
            user_id=user.get_id(),
            limit=self.limit,
            offset=self.offset)]
        for kind in ['artists', 'albums', 'tracks']:
            keys.append(
                cache.make_key(
                    '/favorite/getUserFavorites',
                    user_id=user.get_id(),
                    limit=self.limit,
                    type=kind,
                    offset=self.offset))
        ret = False
        for key in keys:
            if cache.delete(key):
                ret = True
        return ret

    def del_track(self, track_id):
        if api.favorite_delete(track_ids=track_id):
            self._delete_cache()
            return True
        return False

    def del_album(self, album_id):
        if api.favorite_delete(album_ids=album_id):
            self._delete_cache()
            return True
        return False

    def del_artist(self, artist_id):
        if api.favorite_delete(artist_ids=artist_id):
            self._delete_cache()
            return True
        return False

    def gui_remove(self):
        qnt, qid = int(self.get_parameter('qnt')), self.get_parameter('qid')
        node = getNode(qnt, {'nid': qid})
        ret = None
        if qnt & Flag.TRACK == Flag.TRACK:
            ret = self.del_track(node.nid)
        elif qnt & Flag.ALBUM == Flag.ALBUM:
            ret = self.del_album(node.nid)
        elif qnt & Flag.ARTIST == Flag.ARTIST:
            ret = self.del_artist(node.nid)
        else:
            raise exception.InvalidNodeType(self.nt)
        if not ret:
            notifyH(dialogHeading,
                    'Cannot remove item: %s' % (node.get_label()))
            return False
        notifyH(dialogHeading,
                'Item successfully removed: %s' % (node.get_label()))
        url = self.make_url(nt=self.nt, nid=None, nm=None)
        executeBuiltin(containerUpdate(url, True))
        return True

    def get_image(self):
        image = self.get_image_from_storage()
        if image is None:
            image = super(Node_favorite, self).get_image()
        return image

    def _get_node_storage_filename(self):
        return u'userdata-{user_id}-favorite-{nid}.local'.format(
            user_id=user.get_id(), nid=self.nid)
