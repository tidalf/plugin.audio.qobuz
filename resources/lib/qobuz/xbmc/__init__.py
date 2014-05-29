# -*- coding: utf-8 -*-
'''
    qobuz.xbmc
    ~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
__all__ = ['settings', 'ItemFactory', 'Player']

import sys

from xbmcpy.mock import xbmcaddon
from xbmcpy.mock.xbmcplugin import xbmcplugin
from xbmcpy.mock.xbmcgui import xbmcgui
from qobuz.node.flag import Flag
from node import Mode
from qobuz.debug import warn
from xbmcpy.util import containerUpdate, lang, runPlugin
from collections import defaultdict
from qobuz.settings import settings as qobuz_settings


class Settings(object):

    def __init__(self, qobuz):
        self.qobuz = qobuz

    def get(self, key, **ka):
        return self.qobuz[key]

    def set(self, key, value, **ka):
        self.qobuz[key] = value

    def __getitem__(self, *a, **ka):
        v = xbmcaddon.Addon().getSetting(a[0])
        if v:
            return v
        try:
            return self.qobuz[a[0]]
        except:
            return None

    def __setitem__(self, *a, **ka):
        self.qobuz[a[0]] = a[1]

    def __iter__(self):
        return self.qobuz.__iter__()

    def __len__(self, *a, **ka):
        return self.qobuz.__len__()

settings = Settings(qobuz_settings)

base_url = 'plugin://%s/' % (xbmcaddon.Addon().getAddonInfo('id'))


def furl(frag):
    return base_url + frag


class ItemFactory(object):

    def __init__(self):
        self.append_context = True

    def menu_from_action(self, menu, node):
        for action in sorted(node.actions):
            ka = {'action': action}
            if 'target' in node.actions[action]:
                ka['target'] = node.actions[action]['target']
            url = furl(node.url(**ka))
            menu.append((node.actions[action]['label'], containerUpdate(url)))

    def make_item(self, node):
        sflag = Flag.to_s(node.kind)
        if sflag in ['track', 'artist']:
            item = getattr(self, 'make_item_%s' % sflag)(node)
        else:
            item = self.make_item_default(node)
        if not item:
            return None
        if self.append_context:
            menu = []
            self.menu_from_action(menu, node)
#            skind = Flag.to_s(node.kind)
#            methname = 'attach_context_%s' % skind
#            if hasattr(self, methname):
#                getattr(self, methname)(menu, node)
#            else:
#                self.attach_context_default(menu, node)
            item.addContextMenuItems(menu, False)
        return item

    def make_item_default(self, node):
        if node is None:
            return None
        label = node.get_label()
        image = node.get_image()
        url = furl(node.url())
        item = xbmcgui.ListItem(label, label, image, image, url)
        return item

    def attach_context_default(self, menu, node):
        """
            Note: Url made with make_url must set mode (like mode=Mode.VIEW)
            else we are copying current mode (for track it's Mode.PLAY ...)
        """
#        colorCaution = getSetting('item_caution_color')
#        url = node.url(kind=Flag.ROOT, mode=Mode.VIEW)
#        menu.append( ('Qobuz', containerUpdate(url, False)) )
#
#        ''' ARTIST '''
        if node.kind & (Flag.ALBUM | Flag.TRACK | Flag.ARTIST):
            artist_id = node.get_artist_id()
            artist_name = node.get_artist()
            url = furl(node.url(kind=Flag.ARTIST, nid=artist_id,
                                mode=Mode.VIEW))
            menu.append(("%s %s" % (lang(32000), artist_name),
                          containerUpdate(url)))

            ''' Similar artist '''
            url = furl(node.url(kind=Flag.ARTIST_SIMILAR, nid=artist_id,
                                     mode=Mode.VIEW))
            menu.append(('%s: %s' % (lang(30010), artist_name),
                          containerUpdate(url)))

#        ''' FAVORITES '''
#        wf = node.kind & (~Flag.FAVORITES)
#        if node.parent:
#            wf = wf and node.parent.kind & ~Flag.FAVORITES
#        if wf:
#            ''' ADD TO FAVORITES / TRACKS'''
#            url = furl(node.url(kind=Flag.FAVORITES,
#                                          action='add_tracks',
#                                          qnid=node.nid,
#                                          qkind=node.kind,
#                                          mode=Mode.VIEW))
#            menu.append( (lang(32001), runPlugin(url) ))
#            ''' ADD TO FAVORITES / Albums'''
#            url = self.make_url(nt=Flag.FAVORITES,
#                                          nm='gui_add_albums',
#                                          qid=self.nid,
#                                          qnt=self.nt,
#                                          mode=Mode.VIEW)
#            menu.add(path='favorites/add_albums',
#                          label=lang(39011) + ' albums', cmd=runPlugin(url))
#            ''' ADD TO FAVORITES / Artists'''
#            url = self.make_url(nt=Flag.FAVORITES,
#                                          nm='gui_add_artists',
#                                          qid=self.nid,
#                                          qnt=self.nt,
#                                          mode=Mode.VIEW)
#            menu.add(path='favorites/add_artists',
#                          label=lang(39011) + ' artists', cmd=runPlugin(url))
#
#        if self.parent and (self.parent.nt & Flag.FAVORITES):
#            url = self.make_url(nt=Flag.FAVORITES,
#                                nm='', mode=Mode.VIEW)
#            menu.add(path='favorites', label="Favorites",
#                     cmd=containerUpdate(url, True),pos=-9)
#            url = self.make_url(nt=Flag.FAVORITES, nm='gui_remove',
#                                qid=self.nid, qnt=self.nt,
#                                mode=Mode.VIEW)
#            menu.add(path='favorites/remove',
#                     label='Remove %s' % (self.get_label()),
#                     cmd=runPlugin(url), color=colorCaution)
#        wf = ~Flag.USERPLAYLISTS
# #        if self.parent:
# #            wf = wf and self.parent.nt & (~Flag.USERPLAYLISTS)
#        if wf:
#            ''' PLAYLIST '''
#            cmd = containerUpdate(self.make_url(nt=Flag.USERPLAYLISTS,
#                                    nid='', mode=Mode.VIEW))
#            menu.add(path='playlist', pos = 1,
#                          label="Playlist", cmd=cmd, mode=Mode.VIEW)
#
#            ''' ADD TO CURRENT PLAYLIST '''
#            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST,
#                                            nm='gui_add_to_current',
#                                            qnt=self.nt,
#                                            mode=Mode.VIEW,
#                                            qid=self.nid))
#            menu.add(path='playlist/add_to_current',
#                          label=lang(39005), cmd=cmd)
#            label = self.get_label()
#            try:
#                label = label.encode('utf8', 'replace')
#            except:
#                warn(self, "Cannot set query..." + repr(label))
#                label = ''
#            label = urllib.quote_plus(label)
#            ''' ADD AS NEW '''
#            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST,
#                                            nm='gui_add_as_new',
#                                            qnt=self.nt,
#                                            query=label,
#                                            mode=Mode.VIEW,
#                                            qid=self.nid))
#            menu.add(path='playlist/add_as_new',
#                          label=lang(30080), cmd=cmd)
#
# #            ''' Show playlist '''
# #            if not (self.nt ^ Flag.USERPLAYLISTS != Flag.USERPLAYLISTS):
# #                cmd = containerUpdate(self.make_url(nt=Flag.USERPLAYLISTS,
# #                                    id='', mode=Mode.VIEW))
# #                menu.add(path='playlist/show',
# #                          label=lang(39006), cmd=cmd)
#
#        ''' PLAYLIST / CREATE '''
#        cFlag = (Flag.PLAYLIST | Flag.USERPLAYLISTS)
#        if self.nt | cFlag == cFlag:
#            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST,
#                                          nm="gui_create", mode=Mode.VIEW))
#            menu.add(path='playlist/create',
#                          label=lang(39008), cmd=cmd)
#        ''' VIEW BIG DIR '''
#        cmd = containerUpdate(self.make_url(mode=Mode.VIEW_BIG_DIR))
#        menu.add(path='qobuz/big_dir',
#                          label=lang(39002), cmd=cmd)
#        ''' SCAN '''
#        if getSetting('enable_scan_feature', isBool=True):
#            query = urllib.quote_plus(self.make_url(mode=Mode.SCAN))
#            url = self.make_url(nt=Flag.ROOT, mode=Mode.VIEW,
#                                nm='gui_scan', query=query)
#            menu.add(path='qobuz/scan',
#                            cmd=runPlugin(url),
#                            label='scan')
#        if self.nt & (Flag.ALL & ~Flag.ALBUM & ~Flag.TRACK
#                        & ~Flag.PLAYLIST):
#            ''' ERASE CACHE '''
#            cmd = runPlugin(self.make_url(nt=Flag.ROOT, nm="cache_remove",
#                                      mode=Mode.VIEW))
#            menu.add(path='qobuz/erase_cache',
#                          label=lang(31009), cmd=cmd,
#                          color=colorCaution, pos=10)
    def make_item_artist(self, node):
        image = node.get_image()
        url = node.url(mode=Mode.VIEW)
        name = node.get_label()
        item = xbmcgui.ListItem(name,
                                name,
                                image,
                                image,
                                url)
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        item.setPath(url)
        item.setInfo('music', infoLabels={
            'artist': node.get_artist(),
            'comment': node.get_description()
        })
        return item

    def make_item_track(self, node):
        media_number = node.get_media_number()
        if not media_number:
            media_number = 1
        else:
            media_number = int(media_number)
        duration = node.get_duration()
        if duration == -1:
            import pprint
            print "Error: no duration\n%s" % (pprint.pformat(node.data))
        label = node.get_label()
        isplayable = 'true'

        # Disable free account checking here, purchased track are
        # still playable even with free account, but we don't know yet.
        # if qobuz.gui.is_free_account():
        #    duration = 60
        # label = '[COLOR=FF555555]' + label + '[/COLOR]
        # [[COLOR=55FF0000]Sample[/COLOR]]'
        mode = Mode.PLAY
        url = node.url(mode=mode)
        image = node.get_image()
        item = xbmcgui.ListItem(label,
                                label,
                                image,
                                image,
                                url)
        item.setIconImage(image)
        item.setThumbnailImage(image)
        if not item:
            warn(self, "Cannot create xbmc list item")
            return None
        item.setPath(url)
        track_number = node.get_track_number()
        if not track_number:
            track_number = 0
        else:
            track_number = int(track_number)
        mlabel = node.get_property('label/name')
        description = node.get_description()
        comment = ''
        if mlabel:
            comment = mlabel
        if description:
            comment += ' - ' + description
        '''Xbmc Library fix: Compilation showing one entry by track
            We are setting artist like 'VA / Artist'
            Data snippet:
                {u'id': 26887, u'name': u'Interprètes Divers'}
                {u'id': 145383, u'name': u'Various Artists'}
                {u'id': 255948, u'name': u'Multi Interpretes'}
        '''
        artist = node.get_artist()
        if node.parent and hasattr(node.parent, 'get_artist_id'):
            artist_id = str(node.parent.get_artist_id())
            if artist_id in ['26887', '145383', '255948']:
                artist = '%s / %s' % (node.parent.get_artist(), artist)
        desc = description or 'Qobuz Music Streaming'
        item.setInfo(type='music', infoLabels={
                     'count': node.nid,
                     'title': node.get_title(),
                     'album': node.get_album(),
                     'genre': node.get_genre(),
                     'artist': artist,
                     'tracknumber': track_number,
                     'duration': duration,
                     'year': node.get_year(),
                     'comment': desc + ' (aid=' + node.get_album_id() + ')',
                     'lyrics': "Chant down babylon lalalala"
                     })
        item.setProperty('DiscNumber', str(media_number))
        item.setProperty('IsPlayable', isplayable)
        item.setProperty('IsInternetStream', isplayable)
        item.setProperty('Music', isplayable)
        return item
