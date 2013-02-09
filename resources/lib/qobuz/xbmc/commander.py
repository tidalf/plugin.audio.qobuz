'''
    qobuz.xbmc.commander
    ~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from node import Commander
from xbmcpy.util import notifyH, lang, executeBuiltin, containerUpdate, nolang
from xbmcpy.mock.xbmcgui import xbmcgui
from qobuz.node import getNode, Flag
from xbmcpy.mock import xbmcaddon
from qobuz.i8n import _

base_url = 'plugin://%s/' % (xbmcaddon.Addon().getAddonInfo('id'))

class QobuzXbmcCommander(Commander):

    def action_favorite_add_tracks(self, favorite, target):
        dialogHeading = _('Add track(s) to favorite')
        tracks = favorite.list_tracks(target)
        if len(tracks) == 0:
            return False
        ret = xbmcgui.Dialog().select(dialogHeading, [
           track.get_label() for track in tracks
        ])
        if ret == -1:
            return False
        track_ids = ','.join([str(track.nid) for track in tracks])
        if not favorite.add_tracks(track_ids):
            notifyH(dialogHeading, _('Cannot add track(s) to favorite'))
            return False
        notifyH(dialogHeading, len(tracks) + ' track(s) added to favorite')
        return True

    def action_favorite_add_albums(self, favorite, target):
        dialogHeading = _('Add album(s) to favorite')
        albums = favorite.list_albums(target)
        if len(albums) == 0:
            return False
        ret = xbmcgui.Dialog().select(dialogHeading, [
           album.get_label() for album in albums
        ])
        if ret == -1:
            return False
        album_ids = ','.join([str(album.nid) for album in albums])
        if not favorite.add_albums(album_ids):
            notifyH(dialogHeading, _('Cannot add album(s) to favorite'))
            return False
        notifyH(dialogHeading, '%s album(s) added to favorite' % len(albums))
        return True

    def action_favorite_add_artists(self, favorite, target):
        dialogHeading = _("Add artist(s) to favorite")
        artists = favorite.list_artists(target)
        if len(artists) == 0:
            return False
        ret = xbmcgui.Dialog().select(dialogHeading, [
           artist.get_label() for artist in artists
        ])
        if ret == -1:
            return False
        artists_ids = ','.join([str(artist.nid) for artist in artists])
        if not favorite.add_artists(artists_ids):
            notifyH(dialogHeading, _('Cannot add album(s) to favorite'))
            return False
        notifyH(dialogHeading, '%s artist(s) added to favorite' % len(artists))
        return True

    def action_similar_artist_get(self, plugin, node, tnode):
        if not hasattr(node, 'get_artist_id'):
            return False
        tnode.nid = node.get_artist_id()
        url = '%s%s' % (base_url, tnode.url())
        executeBuiltin(containerUpdate(url))
        return True
