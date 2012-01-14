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
import random

from debug import log, info, warn
from utils.icacheable import ICacheable

class QobuzGenreImage(ICacheable):

    def __init__(self, Core):
        self.Core = Core
        super(QobuzGenreImage, self).__init__(self.Core.Bootstrap.cacheDir,
                                                     'images-genres')
        self.set_cache_refresh(-1)
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()
        
    def _fetch_data(self):
        return {}

    def set(self, type, genre_id, image):
        data = self.get_data()
        name = str(type) + '-' + str(genre_id)
        data[name] = image
        self._save_cache_data(data)
    
    def get(self, type, genre_id):
        genre_id = str(type) + '-' + str(genre_id)
        data = self.get_data()
        if genre_id in data:
            return data[genre_id]
        return self.Core.Bootstrap.Images.genre(0)