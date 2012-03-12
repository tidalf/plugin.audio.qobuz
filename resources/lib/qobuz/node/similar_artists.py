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
        return "Similar artist"
    
    def get_label2(self):
        return ""
        
    '''
        Build Down
    '''
    def _build_down(self, lvl, flag = None):
        print "ID: " + self.get_id()
        query = self.get_parameter('query')
        print "URL machin: " + query
        data = qobuz.api.get_similar_artists(query)
        print "RESULT: "
        pprint.pformat(data)
        matches = re.findall("<name>(.*)</name>", data)
        
        listid = {}
        for name in matches:
            namec = name.encode('utf8', 'replace').strip().lower()
            print "Artist: " + namec
            #qobuz.gui.notifyH('Qobuz search artist',  name, None, 500)
            search_cache = Cache_search_artists(name)
            result = search_cache.fetch_data()
            if not result or len(result) < 1:
                print "No result for artist: " + namec
                continue
            #print "RESULT: " + pprint.pformat(result['results'])
            for jartist in result:
                    artist = Node_artist()
                    print "JARTIST: " + pprint.pformat(jartist)
                    artist.set_data(jartist)
                    self.add_child(artist)
            
            
    '''
        Get Xbmc ITEMS
    '''
    def _get_xbmc_items(self, list, lvl, flag):
        import qobuz
        if len(self.get_childs()) < 1:
            return False
        for child in self.get_childs():
            if self.filter(flag): continue
            item = child.make_XbmcListItem()
            self.attach_context_menu(item, child)
            list.append((child.get_url(), item, child.is_folder()))
        return True
    
    '''
        Make XbmcListItem
    '''
    def make_XbmcListItem(self):
        item = xbmcgui.ListItem(self.get_label(),
                                self.get_label(),
                                self.get_image(),
                                self.get_image(),
                                self.get_url(),
                                )
        return item

