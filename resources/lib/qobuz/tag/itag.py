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

from debug import info, warn, error

class ITag(object):
    
    def __init__(self):
        self._valid_tags = None
        self._json = None
        self.cache = None
        self.id = None
    
    def set_id(self, id):
        info(self, "Set_id: " + str(id))
        if not id: self.id = None
        if self.id != id: self.id = id
        return self.id
    
    def get_raw_data(self):
        return self._json
    
    def parse_json(self, json):
        assert("load_json must be overloaded")
    
    def set_valid_tags(self, tags):
        self._valid_tags = tags
    
    def get_valid_tags(self):
        return self._valid_tags
    
    def get_json(self):
        if self.cache:
            return self.cache.get_data()
        return self._json
    
    def set_json(self, json):
        self._json = json
        if json:
            self.parse_json(self._json)
    
    def fetch(self):
        info(self, "Fetching data")
        if not self.cache: 
            warn(self, "Print cache is not set get, cannot fetch data!")
            return False
        data = self.cache.fetch_data()
        if not data:
            warn(self, "Cannot fetch data from cache")
            return False
        print repr(data)
        self.parse_json(data)
        return True
        
    def get(self, key):
        if not self.is_loaded():
            assert("Json is not loaded")
        if key not in self._valid_tags:
            assert("Invalid tag: " + key)
        return self.__dict__[key]
    
    def set(self, key, value):
        if key not in self._valid_tags:
            assert("Invalid tag:" + key)
        v = ''
        try:
            v = value.encode('utf8', 'ignore')
        except:
            if isinstance(value, basestring):
                v = value.encode('utf8', 'ignore')
            elif isinstance(value, bool):
                if value: v = '1'
                else: v = '0'
        if v == 'None':
            return
        self.__dict__[key] = v.decode('utf8', 'ignore')
    
    def auto_parse_json(self, json):
        valid_tags = self.get_valid_tags()
        for tag in valid_tags:
            try:
                self.set(tag, json[tag])
            except:
                pass
        return True

    
    def getXbmcItem(self, fanArt = ''):
        import xbmcgui
        import qobuz
        date = 0
        try:
            date = self.getDate('#').split('#')[0]
        except: data = 0
        year = 0
        if date:
            try:
                year = date.split('-')[0]
            except: pass
        genre = self.getGenre()
        i = xbmcgui.ListItem(self.getTitle())
        i.setLabel(self.getLabel())
        i.setInfo(type='file', infoLabels = {
                                              #'count': pos,
                                             'title': self.getTitle(),
                                             'artist': self.getArtist(),
                                             'genre': self.getGenre(),
                                             'album': self.getAlbum(),
                                             'year': int(year),
                                             'comment': 'Qobuz Music Streaming (qobuz.com)'
                                             })
        i.setProperty('qobuz_id', self.id)
        i.setProperty('reponame', "plop")
        i.setProperty("IsPlayable", "false")
        if fanArt:
            i.setProperty('fanart_image', qobuz.image.access.get(fanArt))
        image = self.getImage()
        if image:
            i.setThumbnailImage(image)
            i.setIconImage(image)
        qobuz.gui.setContextMenu(i)
        return i
