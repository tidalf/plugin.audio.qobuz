#!/usr/bin/python
import httplib, json,time,urllib2,urllib,hashlib,mutagen
from mutagen.flac import FLAC
# import os,sys,re,string,array
# import playlist
class Api:
    def __init__(self, qob):
    	self.qob = qob
	self.headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        self.authtoken = None 
        self.userid = None

    def _api_request(self,params, uri):
        self.conn = httplib.HTTPConnection("player.qobuz.com")
        self.conn.request("POST", uri, params, self.headers)
        response = self.conn.getresponse()
        response_json = json.loads(response.read())
        return response_json

    def get_track_url(self,track_id,context_type,context_id):
   		params = urllib.urlencode({'x-api-auth-token':self.authtoken,'track_id': track_id ,'format_id':6,'context_type':context_type,'context_id':context_id})
	# add try catch here
		done=False
		while done == False:
			try:
				data = self._api_request(params,"/api.json/0.1/track/getStreamingUrl")
				done = True
			except: 
				print "try again"
		# xbmc.log(json.dumps(data))
   		url=data[u'streaming_url']
		return url
    
    
    def get_track(self,trackid):
		params = urllib.urlencode({'x-api-auth-token':self.authtoken,'track_id': trackid})
		data = self._api_request(params,"/api.json/0.1/track/get")
		return data
     
    def get_playlists(self):
   		params = urllib.urlencode({'x-api-auth-token':self.authtoken,'user_id': self.userid})
   		data = self._api_request(params,"/api.json/0.1/playlist/getUserPlaylists")
		return self._parsePlaylists(data)

    def _parsePlaylists(self, items):
    	i = 0
        list = []
        #if 'playlist' in data:
        #       playlists = items['result']['playlists']
        #elif len(items) > 0:
        #       playlists = items
        #else:
        #       return []

        #while (i < len(playlists)):
        # print json.dumps(items)
        for playlist in items:
        # s = playlists[i]
			list.append([playlist['playlist']['name'].encode('ascii', 'ignore'), playlist['playlist']['id']])
        #i = i + 1
        return list
    
	def getPlaylistSongs(self, playlistID):
		result = self._callRemote('getPlaylistSongs', {'playlistID' : playlistID});
		if 'result' in result:
			return self._parseSongs(result)
		else:
			return []
    
    def login(self,user,password):
        params = urllib.urlencode({'x-api-auth-token':'null','email': user ,'hashed_password': hashlib.md5(password).hexdigest() })
   	data = self._api_request(params,"/api.json/0.1/user/login")
        if not 'user' in data:
		return None
	self.authtoken = data['user']['session_id']	
        self.userid = data['user']['id']	
        return self.userid 

    def get_tracks(self, playlist_id=39837):
	params = urllib.urlencode({'x-api-auth-token':self.authtoken,'playlist_id':playlist_id,'extra':'tracks'})
        return self._api_request(params,"/api.json/0.1/playlist/get")
    
    def get_album_tracks(self, album_id):
	params = urllib.urlencode({'x-api-auth-token':self.authtoken,'product_id':album_id})
        return self._api_request(params,"/api.json/0.1/product/get")

class Qobuz:
    def __init__(self):
	self.data = ""
	self.conn = ""
	self.Api = Api(self) 

    def login(self, user, password):
            return self.Api.login(user,password)

    def is_logged(self):
            return self.Api.userid

    def download_track_withurl(self,file_name,url):
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)
        file_size_dl = 0
        block_sz = 8192
        while True:
         buffer = u.read(block_sz)
         if not buffer:
                break
         file_size_dl += len(buffer)
         f.write(buffer)
         status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
         status = status + chr(8)*(len(status)+1)
         print status,
        f.close()
        u.close()

    def getPlaylist(self, id):
    	return Playlist(self, id)

    
    def getAlbum(self, id):
    	return Album(self, id)
    
    def tag_track(self,track,file_name,album_title="null"):
		audio = FLAC(file_name)
		audio["title"] = track['title']
		
		if album_title == "null":
			audio["album"] = track['album']['title']
			audio["genre"] = track['album']['genre']['name']
			audio["date"] = track['album']['release_date']
		else:
			audio["album"] = album_title
		
		#audio["genre"] = self.pdata['product']['genre']['name']
		#audio["date"] = self.pdata['product']['release_date'] 
  		
  		audio["length"] = track['duration']
   		audio["artist"] = track['interpreter']['name']
   		audio["discnumber"] = track['media_number']
		audio["tracknumber"] = track['track_number']
		audio.pprint()
		audio.save()
    
    
    def download_track(self,track,context,context_id,album_title="null"):
		url=self.Api.get_track_url(track['id'],context,context_id) 
		if album_title == "null":
			track_album=track['album']['title']
		else:
			track_album=album_title 
		file_name = track['interpreter']['name'] +" - "+ track_album + " - "+track['track_number']+" - "+track['title']+".flac"
		self.download_track_withurl(file_name,url)
		if album_title != "null":
			self.tag_track(track,file_name,album_title)
		else:
			self.tag_track(track,file_name)

class Playlist:
	def __init__(self,qob,playlist_id):
		self.qob = qob
		self.playlist_id = playlist_id
		self.conn = ""
		self.pdata = self.qob.Api.get_tracks(playlist_id)

	def download_all(self):
		for track in self.pdata['playlist']['tracks']:
			self.qob.download_track(track,'playlist',self.playlist_id)
		#	print "\nsleeping 5s"
			time.sleep(5)

	def print_tracks (self):
		for track in self.pdata['playlist']['tracks']:
			print track['interpreter']['name'] +" - "+ track['album']['title'] + " - "+track['track_number'] +" - " + track['title']

	def getPlaylistSongs(self, playlistID):
		# result = self._callRemote('getPlaylistSongs', {'playlistID' : playlistID});
		return self._parseSongs(result)
			
	def parseSongs(self):
		#	if 'CoverArtFilename' not in s:
		#		info = self.getSongsInfo(s['SongID'])
		#		coverart = info['CoverArtFilename']
		#	elif s['CoverArtFilename'] != None:
		#		coverart = THUMB_URL+s['CoverArtFilename'].encode('ascii', 'ignore')
		#	else:
		list = []
		for track in self.pdata['playlist']['tracks']:
			coverart = 'None'
			if track['interpreter']['name']:
				artist=track['interpreter']['name'].encode('ascii', 'ignore')
			else:
				artist=track['interpreter']['name']
	
			list.append([track['title'].encode('ascii', 'ignore'),track['id'],track['album']['title'].encode('ascii', 'ignore') ,track['album']['id'],artist,track['interpreter']['id'],coverart])
		return list
			

class Album:
    def __init__(self,qob,album_id):
        self.qob = qob
	self.album_id = album_id
        self.conn = ""
	self.pdata = self.qob.Api.get_album_tracks(album_id)

    def download_all(self):
	for track in self.pdata['product']['tracks']:
		self.qob.download_track(track,'album',self.album_id,self.pdata['product']['title'])
   		print "\nsleeping 5s"
   		time.sleep(5)

    def print_tracks (self):
	for track in self.pdata['product']['tracks']:
		#		print json.dumps(track)
   		print track['interpreter']['name'] +" - "+ self.pdata['product']['title'] + " - "+track['track_number'] +" - " + track['title']