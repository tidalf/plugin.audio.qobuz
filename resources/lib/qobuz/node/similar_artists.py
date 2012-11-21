#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
import sys
import pprint

import xbmcgui

import qobuz
from constants import Mode

from flag import NodeFlag
from node import Node
from artist import Node_artist
from debug import info, warn, error, debug
from cache.search_artists import Cache_search_artists
import urllib
import re
from xml.dom.minidom import parse, parseString
'''
    NODE ARTIST
'''

class Node_similar_artist(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_similar_artist, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_SIMILAR_ARTIST
        self.set_content_type('albums')
        

    '''
        Getter 
    '''
    def get_label(self):
        return qobuz.lang(39000)
    
    def get_label2(self):
        return ""
        
    '''
        Build Down
    '''
    def _build_down(self, xbmc_directory, lvl, flag = None):
        query = self.get_parameter('query').strip().lower()
        query.encode('utf8', 'replace')
        data = qobuz.api.get_similar_artists(query)
        warn (self, pprint.pformat(data))
        if not data: return False
        #dom = parseString(data)
        class parse_simartists():
            def __init__(self, data):
                self.dom = parseString(data)
                self.artists = []
            def getText(self, nodelist):
                    rc = []
                    for node in nodelist:
                        if node.nodeType == node.TEXT_NODE:
                            rc.append(node.data)
                    return ''.join(rc)
            def parse(self):
                self._get_artists(self.dom)
        
            def _get_artists(self, dom):
                artists = dom.getElementsByTagName('artist')
                for artist in artists:
                    self._h_artist(artist)
            def _h_artist_image(self, domlist, artist):
                for dom in domlist:
                    size = dom.getAttribute('size')
                    if size != 'mega': continue
                    image = self.getText(dom.childNodes)
                    artist['image'] = image
            def _h_artist(self, dom):
                name = self.getText(dom.getElementsByTagName('name')[0].childNodes).strip().lower()
                artist = { 'name': name}
                self._h_artist_image(dom.getElementsByTagName('image'), artist)
                self.artists.append(artist)
                return True
        parse = parse_simartists(data)
        parse.parse()
        
        if len(parse.artists) < 1:
            qobuz.gui.notifyH("Qobuz: No similar artist", urllib.unquote(query))
            return False
        listid = {}
        max = 20
        count = 0
        total = len(parse.artists)
        for a in parse.artists:
            if count > max: break
            count+=1
            name = a['name']
            if not name:
                continue
            name = name.encode('utf8', 'replace')
            xbmc_directory.update(count, total, qobuz.lang(40005), name)
            if xbmc_directory.is_canceled():
                break
            search_cache = Cache_search_artists(name)
            result = search_cache.fetch_data()
            if not result or len(result) < 1:
                warn(self,  "No result for artist: " + name)
                continue
            for jartist in result:
                artist_id = jartist['id']
                if artist_id in listid:
                    continue
                artist = Node_artist()
                artist.set_data(jartist)
                artist.set_image(a['image'])
                listid[artist_id] = artist 
                self.add_child(artist)
        return len(parse.artists)

