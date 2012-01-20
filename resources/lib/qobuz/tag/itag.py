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

class ITag(object):
    
    def __init__(self, json = None, parent = None):
        self.__valid_tags = None
        self.__is_loaded = None
        self._json = json
        self._parent = parent
        self._childs = []
        
    def add_child(self, child):
        self._childs.append(child)
    
    def get_childs(self):
        return self._childs
    
    def get_childs_with_type(self, otype):
        list = []
        for c in self._childs:
            if isinstance(c, otype):
                continue
            list.append(c)
        return list
    
    def get_parent(self):
        return self._parent
    
    def get_raw_data(self):
        return self._json
    
    def parse_json(self, json):
        assert("load_json must be overloaded")
    
    def set_valid_tags(self, tags):
        self.__valid_tags = tags
    
    def get_valid_tags(self):
        return self.__valid_tags
    
    def get(self, key):
        if not self.is_loaded():
            assert("Json is not loaded")
        if key not in self.__valid_tags:
            assert("Invalid tag: " + key)
        return self.__dict__[key]
    
    def set(self, key, value):
        if key not in self.__valid_tags:
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

    def is_loaded(self):
        return self.__is_loaded
    
    def getTitle(self):
        v = ''
        try: v = self.title
        except: return ''
        return v
    
    def getArtistId(self):
        label = []
        try: 
            label.append(self.artist_id)
        except:
            try:
                label.append(self.interpreter_id)
            except: 
                try:
                    label.append(self.composer_id)
                except: label.append('N/A')
        return ''.join(label)
    
    def getGenre(self, sep = ''):
        genre = ''
        childs = self.get_childs()
        for c in childs:
            genre = c.getGenre(sep)
            if genre: return genre
        return genre
    
    def getImage(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getImage(sep)
            if data: return data
        return data
    
    def getDate(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getDate(sep)
            if data: return data
        return data

    def getAlbum(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getAlbum(sep)
            if data: return data 
        return data
    
    def getAlbumId(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getAlbumId(sep)
            if data: return data 
        return data
    
    def getArtist(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getArtist(sep)
            if data: return data
        return data
    
    def getComposer(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getComposer(sep)
            if data: return data
        return data

    def getInterpreter(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getInterpreter(sep)
            if data: return data
        return data
    
    def getDuration(self, sep = ''):
        data = 0
        childs = self.get_childs()
        for c in childs:
            data = c.getDuration(sep) 
            if data: return data
        return data
    
    def getTitle(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getTitle(sep) 
            if data: return data
        return data
    
    def getOwner(self, sep = ''):
        data = ''
        childs = self.get_childs()
        for c in childs:
            data = c.getOwner(sep) 
            if data: return data
        return data    
    
    def getLabel(self):
        return self.getTitle()
    
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
        genre = ''
        if self.get_parent():
            genre = self.get_parent().getGenre()
        else: genre = self.getGenre()
        i = xbmcgui.ListItem(self.getTitle())
        i.setLabel(self.getLabel())
        i.setInfo(type='music', infoLabels = {
                                              #'count': pos,
                                             'title': self.getTitle(),
                                             'artist': self.getArtist(),
                                             'genre': self.getGenre(),
                                             'album': self.getAlbum(),
                                             'year': int(year),
                                             'comment': 'Qobuz Music Streaming (qobuz.com)'
                                             })
        i.setProperty('qobuz_id', self.id)
        print "Set ID: " + self.id
        i.setProperty("IsPlayable", "false")
        if fanArt:
            i.setProperty('fanart_image', qobuz.image.access.get(fanArt))
        image = self.getImage()
        if image:
            i.setThumbnailImage(image)
            i.setIconImage(image)
        qobuz.gui.setContextMenu(i)
        return i
