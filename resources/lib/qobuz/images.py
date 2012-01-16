import os
from debug import log, info, warn
from utils.icacheable import ICacheable
import qobuz
class QobuzImage_access():

    def __init__(self):
        self.images = {}
        self.add('fanArt',    os.path.join(qobuz.path.base, '..', '..',  'fanart.jpg'))
        self.add('qobuzIcon', os.path.join(qobuz.path.base, 'default.png'))
        self.add('qobuzIconRed', os.path.join(qobuz.path.base, 'default_red.png'))
        
    def add(self, name, filename):
        print 'Add image %s: %s\n' % (name, filename)
        self.images[name] = filename
        
    def get(self, name, path = '', ext = 'png'):
        if name in self.images:
            return self.images[name]
        path = os.path.join(qobuz.path.base, path, name + '.' + ext)
        self.add(name, path)
        return path
    
    def genre(self, name):
        if isinstance(name, int):
            if name == 0:
                name = 'default'
            elif name == 64:
                name = 'electro'
            elif name == 80:
                name = 'jazz'
        return self.get('genre.name', 'genres')
    
    def getFanArt(self):
        return self.fanArt
    
    import random

class QobuzImage_cache(ICacheable):

    def __init__(self):
        super(QobuzImage_cache, self).__init__(qobuz.path.cache,
                                                     'images-genres')
        self.set_cache_refresh(-1)
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()
        
    def _fetch_data(self):
        return {}

    def set(self, type, genre_id, image):
        data = self.get_data()
        name = str(type).strip() + '-' + str(genre_id).strip()
        print "NEW NAME: " + name + ": " + image
        data[name] = image
        self._save_cache_data(data)
        return image
    
    def get(self, type, genre_id):
        genre_id = str(type).strip() + '-' + str(genre_id).strip()
        data = self.get_data()
        if genre_id in data:
            return data[genre_id]
        return ''
    
class QobuzImage():
    
    def __init__(self):
        self.access = QobuzImage_access()
        self.cache = QobuzImage_cache()
