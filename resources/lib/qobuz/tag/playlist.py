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
import pprint                       

from cache.playlist import Cache_playlist

from itag import ITag
from track import Tag_track
from owner import Tag_owner


class Tag_playlist(ITag):
    
    def __init__(self):
        super(Tag_playlist, self).__init__()
        #pprint.pprint(json)
        self.set_valid_tags(['name', 'description', 'id', 'is_collaborative', 'is_public'])
        self.cache = None
        
    def getLabel(self):
        name = self.name
        return name
    
    def get_name(self):
        return self.name
    
    def get_owner(self):
        try: return self.owner.name
        except: return ''
    
    def getIsPublic(self):
        is_public = False
        try:
            pub = self.is_public
            if pub == 'true': is_public = True
        except: pass
        return is_public
    
    def getIsCollaborative(self):
        is_co = False
        try:
            co = self.is_collaborative
            if co == 'true': is_co = True
        except: pass
        return is_co
        
    def getDescription(self):
        desc = ''
        try: desc = self.description
        except: pass
        return desc
    
    def set_id(self, p_id):
        self.set_cache_with_id(p_id)
        return super(Tag_playlist, self).set_id(p_id)
        
    def set_cache_with_id(self, id):
        self.cache = Cache_playlist(id)
    
    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'owner' in p:
            c = Tag_owner()
            c.set_json(p['owner'])
            self.owner = c 
#    def getXbmcItem(self, fanArt = ''):
#        item = super(TagPlaylist, self).getXbmcItem(fanArt)
#        owner = ''
#        if self.getOwner() == 'qobuz':
#            owner = '' + self.getOwner() + ' - '
#            
#        item.setLabel()
#        return item
#        