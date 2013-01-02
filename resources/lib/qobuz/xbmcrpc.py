import json
import xbmc
from exception import QobuzXbmcError


class XbmcRPC:
    def __init__(self):
        pass

    def send(self, request):
        if not request:
            raise QobuzXbmcError(
                who=self, what='missing_parameter', additional='request')
        request['jsonrpc'] = '2.0'
        request['method'] = request['method']
        # if not 'id' in request: request['id'] = 1
        rjson = json.dumps(request)
        ret = xbmc.executeJSONRPC(rjson)
        return ret

    def ping(self):
        request = {
            'method': 'JSONRPC.Ping',
            'id': 1
        }
        return self.send(request)

    def showNotification(self, title, message, image='', displaytime=5000):
        request = {
            'method': 'GUI.ShowNotification',
            'title': title,
            'message': message,
            #                   'image': 'info',
            #                   'displaytime': displaytime
        }
        return self.send(request)
