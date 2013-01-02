import json
import xbmc
from exception import QobuzXbmcError

def showNotification(title, message, image = None, mstime = 1000):
    rpc = XbmcRPC()
    return rpc.showNotification(title, message, image, mstime)

class XbmcRPC:
    def __init__(self):
        pass

    def send(self, request):
        if not request:
            raise QobuzXbmcError(
                who=self, what='missing_parameter', additional='request')
        request['jsonrpc'] = '2.0'
        request['method'] = request['method']
        rjson = json.dumps(request)
        ret = xbmc.executeJSONRPC(rjson)
        return ret

    def ping(self):
        request = {
            'method': 'JSONRPC.Ping',
            'id': 1
        }
        return self.send(request)

    def showNotification(self, title, message, image=None, displaytime=5000):
        request = {
            'method': 'GUI.ShowNotification',
            'params': {
                       'title': title,
                       'message': message
            }
        }
        if image:
            request['params']['image'] = image
        if displaytime:
            request['params']['displaytime'] = displaytime
        return self.send(request)


