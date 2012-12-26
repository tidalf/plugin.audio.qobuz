class QobuzApiData:
    services = {
    'user': {
             'login': {
                       'parameters': {
                                      'app_id'  : { 'required': True,'type': 'int'     },
                                      'username': { 'required': True,'type': 'string' },
                                      'email'   : { 'required': False,'type': 'string' },
                                      'password': { 'required': True,'type': 'string'  }
                                      }
                      }
            }
    }
    
    def __init__(self,*a,**ka):
        self.data = ka

from exception import QobuzXbmcError

class QobuzRequest:
    data = QobuzApiData()

    def __init__(self,*a,**ka):
        self.options = ka

    def get(self,*a, **ka):
        if not 'query' in ka: return None

    def send(self, **ka):
        if not 'query' in ka: raise QobuzXbmcError(who=self, what='missing_parameter', additional='query');

if __name__ == '__main__':
    req = QobuzRequest()
    req.send()