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

from itag import ITag
from track import Tag_track
from owner import Tag_owner

class TagPlaylist(ITag):
    
    def __init__(self, json, parent = None):
        super(TagPlaylist, self).__init__(json, parent)
        #pprint.pprint(json)
        self.set_valid_tags(['name', 'description', 'id', 'is_collaborative', 'is_public'])
        if json: self.parse_json(json)
    
    def getLabel(self):
        name = self.name
        return name
    
    def getName(self):
        return self.name
    
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
    
    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'owner' in p:
            c = TagOwner(p['owner'])
            self.add_child(c)
        self.set('owner', p['owner']['name'])
        if not 'tracks' in p:
            return 
        for track in p['tracks']:
            self.add_child(TagTrack(track, self))
        self._is_loaded = True
    
#    def getXbmcItem(self, fanArt = ''):
#        item = super(TagPlaylist, self).getXbmcItem(fanArt)
#        owner = ''
#        if self.getOwner() == 'qobuz':
#            owner = '' + self.getOwner() + ' - '
#            
#        item.setLabel()
#        return item
#        