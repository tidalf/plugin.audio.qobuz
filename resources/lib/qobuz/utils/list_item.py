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
from debug import warn, log, error
from data.track_streamurl import QobuzTrackURL
from data.track import QobuzTrack
from utils.tag import QobuzTagTrack

class QobuzListItem(object):
    def __init__(self):
        pass
        
class QobuzListItem_track(QobuzListItem):
    def __init__(self, track_id):
        #super(QobuzListItem_track, self).__init__()
        self.stream_url = None
        self.stream_format = None
        self.stream_format_id = None
        self.req_stream_format = None
        self.req_stream_format_id = None
        self.mimetype = None
        self.track_id = track_id
        self.stream_type = None
        self.display_context = 'album'
        self.fanart_image = ''
        
    def set_requ_stream(self, format = 'flac'): 
        sfid = None
        if format == 'flac':
            sfid = 6
        elif  format == 'mp3':
            sfid = 5
        else:
            error(self, "Invalid stream format requested: " + format)
            return False
        self.req_stream_format = format
        self.req_stream_format_id = sfid
        return True
    
    def set_requ_stream_id(self, id):
        id = int(id)
        sf = None
        sfid = None
        if id == 6:
            sf = 'flac'
            sfid = 6
        elif id == 5:
            sf = 'mp3'
            sfid = 5
        else:
            error(self, "Invalid stream format requested: " + str(id))
            return False
        self.req_stream_format = sf
        self.req_stream_format_id = sfid
        return True

    def set_stream_url(self, format_id, url, stream_type):
        format_id = int(format_id)
        sf = None
        sfid = None
        mime = None
        if format_id == 6:
            sf = 'flac'
            sfid = 6
            mime = 'audio/flac'
        elif format_id == 5:
            sf = 'mp3'
            sfid = 5
            mime = 'audio/mpeg'
        else:
            error(self, "Unknow format_id from Qobuz: " + str(format_id))
        self.stream_url = url
        self.mimetype = mime
        self.stream_format = sf
        self.stream_format_id = sfid
        self.stream_type = stream_type
        return True
        
    def fetch_stream_url(self, stream_type):
        self.set_requ_stream(stream_type)
        if not self.track_id:
            error(self, "Track id not set")
        if not self.req_stream_format_id:
            error(self, "No stream format id set...")
        turl = QobuzTrackURL(self.track_id, self.req_stream_format_id)
        data = turl.get_data()
        if not data:
            warn(self, "Cannot fetch streaming url for track: " 
                 + str(self.track_id))
            return False
        pprint.pprint(data)
        return self.set_stream_url(data['format_id'], data['streaming_url'], data['streaming_type'])
        
    def get_stream_url(self):
        return self.stream_url
    
    def get_xbmc_list_item(self):
        track = QobuzTrack(self.track_id)
        data = track.get_data()
        if not data:
            warn(self, "Cannot get track data")
            return False
        tag = QobuzTagTrack(data)
        item = tag.getXbmcItem(self.display_context, 0, 'fanArt')
        item.setPath(self.stream_url)
        item.setProperty('streaming_url', self.stream_url)
        item.setProperty('streaming_type', self.stream_type)
        item.setProperty('streaming_format', str(self.stream_format_id))
        item.setProperty('mimetype', self.mimetype)
        item.setProperty('IsPlayable', 'true')
        return item
        
    def to_s(self):
       return pprint.pformat(self.__dict__)