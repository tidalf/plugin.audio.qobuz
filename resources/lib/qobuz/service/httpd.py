import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import pri
import re
import sys
import socket
username = password = base_path = None
cache_duration_long = 60*60*24*365
cache_duration_middle = 60*60*24*365
__image__ = ''

def __xbmc_abort_requested ():
    return False

xbmc_abort_requested = __xbmc_abort_requested()

try:
    import xbmcaddon, xbmcplugin, xbmc
    import os
    pluginId = 'plugin.audio.qobuz'
    __addon__ = xbmcaddon.Addon(id=pluginId)
    __addonversion__ = __addon__.getAddonInfo('version')
    __addonid__ = __addon__.getAddonInfo('id')
    __cwd__ = __addon__.getAddonInfo('path')
    dbg = True
    addonDir = __addon__.getAddonInfo('path')
    libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
    qobuzDir = xbmc.translatePath(os.path.join(libDir, 'qobuz'))
    sys.path.append(libDir)
    sys.path.append(qobuzDir)
    from bootstrap import QobuzBootstrap
    import qobuz
    __handle__ = -1
    boot = QobuzBootstrap(__addon__, __handle__)
    boot.bootstrap_directories()
    boot.bootstrap_registry()
    username = __addon__.getSetting('username')
    password = __addon__.getSetting('password')
    base_path = qobuz.path.cache
    def __abort_requested():
        return xbmc.abortRequested
    xbmc_abort_requested = __abort_requested()
    print "XBMC INIT DONE"
except Exception as e:
    print "Raise %s" % (repr(e))
    #raise e
    username = 'YOUR_USERNAME'
    password = 'YOUR_PASSWORD'
    base_path = 'CACHE_BASE_PATH'
finally:
    print "%s / %s (%s)" % (username, password, base_path)
    if not (username or password or base_path):
        raise Exception("Missing Mandatory Parameter")
from node.track import Node_track
from registry import QobuzRegistry
from debug import log

qobuz.registry = QobuzRegistry(
                cacheType='default',
                username=username,
                password=password,
                basePath=base_path,
                streamFormat=5, 
                hashKey=True,
                cacheMiddle=cache_duration_middle,
                cacheLong=cache_duration_long
            )

class XbmcAbort(Exception):
    def __init__(self, *a, **ka):
        super(XbmcAbort, self).__init__(*a, **ka)
 
class BadRequest(Exception):
    def __init__(self, *a, **ka):
        self.code = 400
        self.message = 'Bad Request '
        super(BadRequest, self).__init__(*a, **ka)
               
class Unauthorized(Exception):
    def __init__(self, *a, **ka):
        self.code = 401
        self.message = 'Unauthorized '
        super(Unauthorized, self).__init__(*a, **ka)

class RequestFailed(Exception):
    def __init__(self, *a, **ka):
        self.code = 402
        self.message = 'Request Failed'
        super(RequestFailed, self).__init__(*a, **ka)
        
class ServerErrors(Exception):
    def __init__(self, *a, **ka):
        self.code = 500
        self.message = 'Server errors'
        super(ServerErrors, self).__init__(*a, **ka)

class QobuzResponse:
    
    def __init__(self, request):
        self.request = request
        self.type = None
        self.id = None
        self.fileExt = None
        self.__parse_path(request.path)

    @property
    def path(self):
        return self._path
    @path.getter
    def path(self):
        return self._path
    @path.setter
    def path(self, value):    
        self.reset_request()
        self.__parse_path(value)
        self._path = value

    def reset_request(self):
        self.path = None
        self.type = None
        self.id = None
        self.fileExt = None

    def __parse_path_track(self, path):
        m = re.search('^/qobuz/track/(\d+)(.*)$', path)
        if not m: 
            return False
        self.id = m.group(1)
        self.fileExt = m.group(2)
        self.type = 'track'

    def __parse_path(self, path):
        if path.startswith("/qobuz/track/"):
            return self.__parse_path_track(path)
        return False

    def has_audio_file_ext(self):
        if not self.fileExt:
            return False
        if not (self.fileExt == '.mp3' or self.fileExt == '.flac'):
            return False
        return True

class QobuzHttpResolver_Handler(BaseHTTPRequestHandler):

    def __check_local_request(self):
        host, port = self.client_address
        if host != '127.0.0.1':
            raise Unauthorized()

    def check_client(self):
        self.__check_local_request()

    def do_GET(self):
        try:
            self.check_client()
            request = QobuzResponse(self)
            if request.type == 'track' and request.has_audio_file_ext():
                node = Node_track(None, {'nid': request.id})
                streaming_url = node.get_streaming_url()
                if not streaming_url:
                    raise RequestFailed()
                self.send_response(303, "Resolved")
                self.send_header('location', streaming_url)
                self.end_headers()
                msg = 'OK %s %s' % (self.address_string(), self.path)
                self.log_message(msg)
            else:
                raise BadRequest()
        except BadRequest as e:
            self.send_error(e.code, e.message)
        except Unauthorized as e:
            self.send_error(e.code, e.message)
        except RequestFailed as e:
            self.send_error(e.code, e.message)
        except Exception as e:
            msg = 'Server errors (%s / %s)\n%s' % (
                                                  sys.exc_type, sys.exc_value,
                                                  repr(e))
            self.log_message(msg)
            self.send_error(500, msg)

    def do_HEAD(self):
        try:
            self.check_client()
            request = QobuzResponse(self)
            if request.type == 'track' and request.has_audio_file_ext():
                self.send_response(200, "Ok ;)")
                self.send_header('content-type', 'audio/flac')
                self.end_headers()
                msg = 'OK %s %s' % (self.address_string(), self.path)
                self.log_message(msg)
            else:
                raise BadRequest()
        except BadRequest as e:
            self.send_error(e.code, e.message)
        except Unauthorized as e:
            self.send_error(e.code, e.message)
        except RequestFailed as e:
            self.send_error(e.code, e.message)
        except Exception as e:
            msg = 'Server errors (%s / %s)\n%s' % (
                                                  sys.exc_type, sys.exc_value,
                                                  repr(e))
            self.log_message(msg)
            self.send_error(500, msg)

class QobuzHttpResolver(HTTPServer):
    
    def abort_requested(self):
        try:
            return xbmc_abort_requested()
        except:
            return False

    def server_forever(self):
        if self.abort_requested():
            raise XbmcAbort()
        super(QobuzHttpResolver, self).serve_forever()

def main():
    try:
        server = QobuzHttpResolver(('', 80), QobuzHttpResolver_Handler)
        log(server, 'Starting...')
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
    except XbmcAbort:
        log(server, 'Received xbmc abort... closing')
    finally:
        server.socket.close()

if __name__ == '__main__':
    main()
