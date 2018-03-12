'''
    qobuz.node.playlist
    ~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from kodi_six import xbmcgui  # pylint:disable=E0401

from .context_menu import attach_context_menu
from .props import propsMap
from qobuz import config
from qobuz import image
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.cache import cache
from qobuz.cache.cache_util import clean_all
from qobuz.constants import Mode
from qobuz.debug import getLogger
from qobuz.gui.contextmenu import contextMenu
from qobuz.gui.util import ask
from qobuz.gui.util import containerRefresh, containerUpdate
from qobuz.gui.util import lang, executeBuiltin
from qobuz.gui.util import notify_warn, notify_error, notify_log
from qobuz.node import getNode, Flag
from qobuz.node.inode import INode
from qobuz.renderer import renderer
from qobuz.theme import theme, color
from qobuz.util.converter import converter

logger = getLogger(__name__)
dialogHeading = 'Qobuz playlist'


def cmp_genre(a, b):
    if a['percent'] < b['percent']:
        return 1
    elif a['percent'] > b['percent']:
        return -1
    return 0


class Node_playlist(INode):
    def __init__(self, parent=None, parameters=None, data=None):
        parameters = {} if parameters is None else parameters
        super(Node_playlist, self).__init__(
            parent=parent, parameters=parameters, data=data)
        self._items_path = 'tracks/items'
        self.b_is_current = False
        self.current_playlist_id = None
        self.is_my_playlist = False
        self.propsMap = propsMap
        self.target_nt = self.get_parameter('nt')

    def get_is_folder(self):
        count = self.get_property('tracks_count')
        if count is not None and count > 0:
            return True
        if self.count() > 0:
            return True
        return False

    def set_is_folder(self, value):
        pass

    is_folder = property(get_is_folder, set_is_folder)

    def _get_node_storage_filename(self):
        return u'userdata-{user_id}-playlist-{nid}.local'.format(
            user_id=user.get_id(), nid=self.nid)

    def get_label(self, default=None):
        return self.label or self.get_name()

    def set_is_my_playlist(self, value):
        self.is_my_playlist = value

    def set_is_current(self, value):
        self.b_is_current = value

    def is_current(self):
        return self.b_is_current

    def _fetch_args(self):
        return ('/playlist/get', {
            'playlist_id': self.nid,
            'offset': self.offset,
            'limit': self.limit,
            'extra': 'tracks'
        })

    def fetch(self, options=None):
        method, args = self._fetch_args()
        return api.get(method, **args)

    def _count(self):
        return len(self.get_property(self._items_path, default=[]))

    def populate(self, options=None):
        if self.count() == 0:
            return False
        for track in self.get_property(self._items_path):
            node = getNode(Flag.TRACK, data=track)
            if not node.get_displayable():
                logger.warn(u'Track not displayable: %s (%s)',
                            node.get_label().encode('ascii', errors='ignore'),
                            node.nid)
                continue
            self.add_child(node)
        return True

    def get_genre(self, first=False, default=None):
        default = [] if default is None else default
        genres = [
            g['name'] for g in sorted(self.get_property('genres'), cmp_genre)
        ]
        if len(genres) == 0:
            return default
        if first:
            return genres[0]
        return genres

    def get_tag(self):
        return u' (tracks: %s, users: %s)' % (self.get_property(
            'tracks_count', to='int'), self.get_property(
            'users_count', to='int'))

    def get_image(self):
        text_size = config.app.registry.get(
            'image_default_size', default='small')
        name = 'images'
        if text_size in ['large', 'xlarge']:
            name = 'images300'
        elif text_size == 'small':
            name = 'images150'
        images = []
        if name in self.data:
            images = self.data.get(name)
        else:  # fallback
            images = self.get_property([
                'images300',
                'images150',
                'images'
            ], default=None)
        if images is None:
            return None
        return image.combine(self.nid, images)

    def makeListItem(self, **ka):
        replaceItems = ka['replaceItems'] if 'replaceItems' in ka else False
        privacy_color = theme.get('item/public/color') if self.get_property(
            'is_public', to='bool') else theme.get('item/private/color')
        tag = color(privacy_color, self.get_tag())
        label = '%s%s' % (self.get_label(), tag)
        if not self.is_my_playlist:
            label = '%s - %s' % (color(
                theme.get('item/default/color'), self.get_owner()), label)
        if self.b_is_current:
            fmt = config.app.registry.get('playlist_current_format')
            label = fmt % (color(theme.get('item/selected/color'), label))
        item = xbmcgui.ListItem(label,
                                self.get_owner(),
                                self.get_image(),
                                self.get_image(), self.make_url())
        if not item:
            logger.warn('Error: Cannot make xbmc list item')
            return None
        item.setArt({'icon': self.get_image(), 'thumb': self.get_image()})
        description = u'''{description}
- owner: {owner}
- tracks: {tracks_count}
- public: {is_public}
- published: {is_published}
- duration : {duration} mn'''.format(
            description=self.get_property(
                'description', default=self.get_property('name')),
            owner=self.get_property(
                'owner/name', default='n/a'),
            tracks_count=self.get_property('tracks_count'),
            is_public=self.get_property('is_public'),
            is_published=self.get_property('is_published'),
            duration=round(
                self.get_property(
                    'duration', default=0.0) / 60.0, 2))
        item.setInfo(
            type='Music', infoLabels={'genre': ', '.join(self.get_genre()), })
        item.setProperty('album_description', description)
        item.setPath(self.make_url())
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item

    def toggle_privacy(self):
        if self.data is None:
            self.data = self.fetch()
        privacy = not self.get_property('is_public', to='bool')
        res = api.playlist_update(
            playlist_id=self.nid, is_public=str(privacy).lower())
        if res is None:
            notify_error('Qobuz', 'Cannot toggle privacy')
            return False
        self.delete_cache(self.nid)
        notify_log(dialogHeading, 'Privacy changed public: %s' % privacy)
        executeBuiltin(containerRefresh())
        return True

    def attach_context_menu(self, item, menu):
        attach_context_menu(self, item, menu)
        super(Node_playlist, self).attach_context_menu(item, menu)

    def remove_tracks(self, tracks_id):
        if not api.playlist_deleteTracks(
                playlist_id=self.nid, playlist_track_ids=tracks_id):
            return False
        return True

    def gui_remove_track(self):
        qid = self.get_parameter('qid')
        if not self.remove_tracks(qid):
            notify_error(dialogHeading, 'Cannot remove track!')
            return False
        self.delete_cache(self.nid)
        notify_log(dialogHeading, 'Track removed from playlist')
        executeBuiltin(containerRefresh())
        return True

    def gui_add_to_current(self):
        cid = self.get_current_playlist()
        qnt = int(self.get_parameter('qnt'))
        qid = self.get_parameter('qid')
        nodes = []
        if qnt & Flag.SEARCH == Flag.SEARCH:
            self.del_parameter('query')
        if qnt & Flag.TRACK == Flag.TRACK:
            node = getNode(qnt, parameters={'nid': qid})
            node.data = node.fetch()
            nodes.append(node)
        else:
            render = renderer(
                qnt,
                parameters=self.parameters,
                depth=-1,
                whiteFlag=Flag.TRACK,
                asList=True)
            render.run()
            nodes = render.nodes
        ret = xbmcgui.Dialog().select('Add to current playlist',
                                      [node.get_label() for node in nodes])
        if ret == -1:
            return False
        ret = self._add_tracks(cid, nodes)
        if not ret:
            notify_warn('Qobuz', 'Failed to add tracks')
            return False
        self.delete_cache(cid)
        notify_log('Qobuz / Tracks added', '%s added' % (len(nodes)))
        return True

    @classmethod
    def _add_tracks(cls, playlist_id, nodes):
        if len(nodes) < 1:
            logger.warn('Empty list...')
            return False
        step = 50
        start = 0
        numtracks = len(nodes)
        if numtracks > 1000:
            notify_error('Qobuz', 'Max tracks per playlist reached (1000)'
                                  '\nSkipping %s tracks' % (numtracks - 1000))
            numtracks = 1000
        while start < numtracks:
            if (start + step) > numtracks:
                step = numtracks - start
            str_tracks = ''
            for i in range(start, start + step):
                node = nodes[i]
                if node.nt != Flag.TRACK:
                    logger.warn('Not a Node_track node')
                    continue
                str_tracks += '%s,' % (str(node.nid))
            if not api.playlist_addTracks(playlist_id=playlist_id,
                                          track_ids=str_tracks):
                return False
            start += step
        return True

    def gui_add_as_new(self, name=None):
        nodes = []
        qnt = int(self.get_parameter('qnt'))
        qid = self.get_parameter('qid')
        name = self.get_parameter('query', to='unquote', default=None)
        if qnt & Flag.SEARCH:
            self.del_parameter('query')
        if qnt & Flag.TRACK == Flag.TRACK:
            node = getNode(qnt, parameters={'nid': qid})
            node.data = node.fetch()
            nodes.append(node)
        else:
            render = renderer(
                qnt,
                parameters=self.parameters,
                depth=-1,
                whiteFlag=Flag.TRACK,
                asList=True)
            render.run()
            nodes = render.nodes
        if len(nodes) == 0:
            return False
        if name is None:
            name = ask('Playlist name? (i8n)')
            if name is None:
                return False
        ret = xbmcgui.Dialog().select('Create playlist %s' % name,
                                      [node.get_label() for node in nodes])
        if ret == -1:
            return False
        playlist = self.create(name)
        if not playlist:
            notify_error('Qobuz', 'Playlist creationg failed')
            logger.warn('Cannot create playlist...')
            return False
        if not self._add_tracks(playlist['id'], nodes):
            notify_error('Qobuz / Cannot add tracks', '%s' % name)
            return False
        self.delete_cache(playlist['id'])
        notify_log('Qobuz / Playlist added', '[%s] %s' % (len(nodes), name))
        executeBuiltin(containerRefresh())
        return True

    def set_as_current(self, playlist_id=None):
        if playlist_id is None:
            playlist_id = self.nid
        if playlist_id is None:
            logger.warn('Cannot set current playlist without id')
            return False
        userdata = self.get_user_storage()
        userdata['current_playlist'] = int(playlist_id)
        if not userdata.sync():
            return False
        executeBuiltin(containerRefresh())
        return True

    def get_current_playlist(self):
        userdata = self.get_user_storage()
        if 'current_playlist' not in userdata:
            return None
        return int(userdata['current_playlist'])

    def gui_rename(self, playlist_id=None):
        if not playlist_id:
            playlist_id = self.nid
        if not playlist_id:
            logger.warn('Can\'t rename playlist without id')
            return False
        node = getNode(Flag.PLAYLIST, parameters={'nid': playlist_id})
        data = node.fetch()
        if not data:
            logger.warn('Something went wrong while renaming playlist')
            return False
        self.data = data
        currentname = self.get_name()
        newname = ask(currentname, lang(30080))
        if newname is None:
            return False
        if newname == '':
            notify_error(dialogHeading, 'Don\'t u call ure child something?')
            return False
        if newname == currentname:
            return True
        res = api.playlist_update(playlist_id=playlist_id, name=newname)
        if not res:
            logger.warn('Cannot rename playlist with name %s' % newname)
            return False
        self.delete_cache(playlist_id)
        notify_log(lang(30080), u'%s: %s' % (lang(30165), currentname))
        executeBuiltin(containerRefresh())
        return True

    @classmethod
    def create(cls, name, isPublic=True, isCollaborative=False):
        return api.playlist_create(
            name=name,
            is_public=converter.bool2str(isPublic),
            is_collaborative=converter.bool2str(isCollaborative))

    def gui_create(self):
        query = self.get_parameter('query', to='unquote')
        if not query:
            query = ask('', lang(30182))
            if query is None:
                logger.warn('Creating playlist aborted')
                return None
            if query == '':
                logger.warn('Cannot create playlist without name')
                return None
        ret = self.create(query)
        if not ret:
            logger.warn('Cannot create playlist named ' ' + query + ' '')
            return None
        self.set_as_current(ret['id'])
        self.delete_cache(ret['id'])
        executeBuiltin(containerRefresh())
        return ret['id']

    def _get_playlist_id(self, playlist_id=None):
        if playlist_id is None:
            playlist_id = self.nid
        return playlist_id

    def gui_set_description(self, playlist_id=None):
        pass

    def gui_remove(self, playlist_id=None):
        playlist_id = self._get_playlist_id(playlist_id=playlist_id)
        if not playlist_id:
            notify_error(dialogHeading,
                         'Invalid playlist %s' % (str(playlist_id)))
            return False
        data = api.get('/playlist/get',
                       playlist_id=playlist_id,
                       limit=self.limit,
                       offset=self.offset)
        if data is None:
            logger.error('Cannot get playlist with id %s', playlist_id)
            return False
        name = ''
        if 'name' in data:
            name = data['name']
        ok = xbmcgui.Dialog().yesno(
            lang(30166), lang(30054), color('FFFF0000', name))
        if not ok:
            return False
        res = False
        if data['owner']['name'] == user.username:
            res = api.playlist_delete(playlist_id=playlist_id)
        else:
            res = api.playlist_unsubscribe(playlist_id=playlist_id)
        if not res:
            logger.warn('Cannot delete playlist with id ' + str(playlist_id))
            notify_error(lang(30183), lang(30186) + name)
            return False
        self.delete_cache(playlist_id)
        executeBuiltin(containerRefresh())
        notify_log(lang(30183), (lang(30184) + '%s' + lang(30185)) % name)
        return True

    def subscribe(self):
        if api.playlist_subscribe(playlist_id=self.nid):
            notify_log(lang(30183), lang(30187))
            self.delete_cache(self.nid)
            return True
        return False

    def delete_cache(self, _playlist_id):
        method, args = self._fetch_args()
        key = cache.make_key(method, **args)
        cache.delete(key)
        clean_all(cache)
        self.remove_node_storage()
