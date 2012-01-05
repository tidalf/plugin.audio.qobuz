import sys
from utils import _sc
from constants import *

class MediaTag():
    def __init__(self, type):
        self.tags = {}
        self.tags['_type'] = type
        self.text = ['name', 'description']
        self.bool = ['is_public', 'is_collaborative']
        self.date = ['created_at', 'updated_at']
        self.int = ['id', 'position']
    
    def getName(self):
        return self.tags['name'] or 'N/A'
    
    def getArtist(self):
        return self.tags['artist'] or 'N/A'
    def getType(self):
        return self.tags['type'] or 'N/A'
    def get_title(self):
        return self.tags['title'] or 'N/A'
    
    def getReleaseDate(self):
        pass
    
    def getId(self):
       pass 
    
    def getDuration(self):
        pass
    def getValue(self, key):
        return self.tags[key] or 'N/A'

    def setValue(self, k, v):
        self.tags[k] = _sc(v)
    
    def getCreatedAt(self):
        if not self.tags['created_at']:
            return [0,0,0,0,0,0]
        (ymd, hms) = self.tags['created_at'].split(' ')
        return ymd.split('-') + hms.split(':')
         

class EasyMediaTag():
    def __init__(self):
        pass
    
    def parse(self, type, json):
        p = None
        if type == 'user_playlists':
            p = QobuzEasyTag_UserPlaylists(json)
            return p.parse()
        else:
            assert("Invalid tag: " + type)
        return p.parse()
        
class EasyMediaTag_UserPlaylists():
    def __init__(self, json):
        self.json = json
        self.list = []
        
    def get_list(self):
        return self.list
    
    def parse(self):
        j = self.json
        for p in self.json:
            t = MediaTag('user_playlists')
            fields = ['id', 'name', 'description', 'position', 'created_at', 'updated_at', 'is_public', 'is_collaborative']
            for f in fields:
                t.setValue(f, p[f])
            t.setValue('owner_name', p['owner']['name'])
            t.setValue('owner_id', p['owner']['id'])
            t.setValue('_url', sys.argv[0] + "?mode=" + str(MODE_PLAYLIST) + "&id=" + t.getValue('id'))
            year = str(t.getCreatedAt()[0])
            t.setValue('title', t.getValue('owner_name') + ' - ' + t.getValue('name') + ' [' + year + ']')
            self.list.append(t)
        return self
            
