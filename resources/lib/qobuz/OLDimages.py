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

import os
from debug import *
from cache.icacheable import ICacheable
import qobuz
import time

class QobuzImage_access():

    def __init__(self):
        self.images = {}
        self.add('fanArt', os.path.join(qobuz.path.image, '..', '..', 'fanart.jpg'))
        self.add('qobuzIcon', os.path.join(qobuz.path.image, 'default.png'))
        self.add('qobuzIconRed', os.path.join(qobuz.path.image, 'default_red.png'))

    def add(self, name, filename):
        self.images[name] = filename

    def get(self, name, path = '', ext = 'png'):
        if name in self.images:
            return self.images[name]
        path = 'file://' + os.path.join(qobuz.path.image, path, name + '.' + ext)
        #path = os.path.join(path, name + '.' + ext)
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
                                                     'images-cache', None, False)
        self.set_cache_refresh(-1)
        debug(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def _fetch_data(self):
        return {}

    def set(self, id, image):
        data = self.get_raw_data()
        data[id] = { 'url': image, 'time': time.time() }
        self._save_cache_data(data)
        return image

    def get(self, id):
        data = self.get_data()
        if id in data and (time.time() - data[id]['time']) < 3600000:
            return data[id]['url']
        return ''

class QobuzImage():

    def __init__(self):
        self.access = QobuzImage_access()
        self.cache = QobuzImage_cache()
