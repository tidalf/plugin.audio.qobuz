'''
    qobuz.xbmc.commander
    ~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from node import Commander
from xbmcpy.util import notifyH, executeBuiltin, containerUpdate
from xbmcpy.util import containerRefresh
from xbmcpy.mock.xbmcgui import xbmcgui
from xbmcpy.mock import xbmcaddon
from qobuz.i8n import _
from qobuz.node import Flag
from xbmcpy.keyboard import Keyboard

base_url = 'plugin://%s/' % (xbmcaddon.Addon().getAddonInfo('id'))


def refresh():
    executeBuiltin(containerRefresh())


class QobuzXbmcCommander(Commander):

    def root_cache_delete_all(self, renderer, root, node):
        dialogHeading = _('Delete all data from cache')
        if not root.cache_delete_all(checkMagic=False):
            notifyH(dialogHeading, 'Fail')
            return False
        notifyH(dialogHeading, 'Success')
        return False

    def root_cache_delete_old(self, renderer, root, node):
        dialogHeading = _('Delete old data from cache')
        if not root.cache_delete_old():
            notifyH(dialogHeading, 'Fail')
            return False
        notifyH(dialogHeading, 'Success')
        return False

    def favorite_add_tracks(self, renderer, favorite, target):
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
        notifyH(dialogHeading, '%s track(s) added to favorite' % len(tracks))
        return False

    def favorite_delete_track(self, renderer, favorite, track):
        dialogHeading = _('Delete track from favorite')
        if not favorite.delete_track(track.nid):
            notifyH(dialogHeading, _('Fail'))
            return False
        notifyH(dialogHeading, _('Success'))
        refresh()
        return False

    def favorite_delete_tracks_from_album(self, renderer, favorite, track):
        dialogHeading = _('Delete tracks from album')
        track.fetch()
        aid = track.get_album_id()
        print "FLAG %s" % Flag.to_s(favorite.kind)
        favorite.items_path = 'tracks'
        tracks = favorite.list_tracks_from_album(aid)
        ret = xbmcgui.Dialog().select(dialogHeading, [
           track.get_label() for track in tracks
        ])
        if ret == -1:
            return False
        track_ids = ','.join([str(track.nid) for track in tracks])
        if not favorite.delete_track(track_ids):
            notifyH(dialogHeading, _('Fail'))
            return False
        notifyH(dialogHeading, _('Success'))
        refresh()
        return False

    def favorite_add_albums(self, renderer, favorite, target):
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
        return False

    def favorite_delete_album(self, renderer, favorite, album):
        dialogHeading = _('Delete album from favorite')
        if not favorite.delete_album(album.nid):
            notifyH(dialogHeading, _('Fail'))
            return False
        notifyH(dialogHeading, _('Success'))
        return True

    def favorite_add_artists(self, renderer, favorite, target):
        dialogHeading = _("Add artist(s) to favorite")
        artists = favorite.list_artists(target)
        print "Add artist %s" % len(artists)
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

    def favorite_delete_artist(self, renderer, favorite, artist):
        dialogHeading = _('Delete artist from favorite')
        if not favorite.delete_artist(artist.nid):
            notifyH(dialogHeading, _('Fail'))
            return False
        notifyH(dialogHeading, _('Success'))
        return True

    def similar_artist_similar(self, renderer, similar_artist, node):
        if not hasattr(node, 'get_artist_id'):
            return False
        similar_artist.nid = node.get_artist_id()
        url = '%s%s' % (base_url, similar_artist.url())
        executeBuiltin(containerUpdate(url))
        return False

    def playlist_new(self, renderer, playlist, userplaylists):
        dialogHeading = _('Create playlist')
        keyboard = Keyboard('', dialogHeading)
        keyboard.doModal()
        if not keyboard.isConfirmed():
            return False
        query = keyboard.getText()
        if not playlist.create(query):
            notifyH(dialogHeading, 'Fail')
            return False
        notifyH(dialogHeading, 'Success')
        return True

    def playlist_rename(self, renderer, playlist, userplaylists):
        dialogHeading = _('Rename playlist')
        playlist.fetch()
        keyboard = Keyboard(playlist.get_label(), dialogHeading)
        keyboard.doModal()
        if not keyboard.isConfirmed():
            return False
        query = keyboard.getText()
        if query == playlist.get_name():
            return False
        if not playlist.rename(query):
            notifyH(dialogHeading, 'Fail')
            return False
        notifyH(dialogHeading, 'Success')
        return True

    def playlist_delete(self, renderer, playlist, none):
        dialogHeading = _('Delete playlist')
        if not playlist.delete():
            notifyH(dialogHeading, 'Fail')
            return False
        notifyH(dialogHeading, 'Success')
        return True

    def albums_by_artist_featured(self, renderer, featured, node):
        node.fetch()
        featured.nid = node.get_artist_id()
        featured.fetch()
        featured.populating(renderer)
        for album in featured:
            renderer.append(album)
        return None

    def artist_similar_list(self, renderer, similar, node):
        node.fetch()
        aid = node.get_artist_id()
        if aid is None:
            return False
        similar.nid = aid
        similar.fetch()
        similar.populating(renderer)
        for artist in similar:
            renderer.append(artist)
        return None
