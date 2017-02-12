import requests
import json
from qobuz import debug

def json_exec(parameters, mid=1, method='Addons.ExecuteAddon',
              addonid='plugin.audio.qobuz', wait=True):
    return json.dumps({
        "jsonrpc": "2.0",
        "id": mid,
        "method": method,
        "params": {
            "params": parameters,
            "wait": wait,
            "addonid": addonid,
        }
    })

def call(parameters, host='127.0.0.1', port=8080):
    debug.info(__name__, 'Call')
    data = json_exec(parameters)
    debug.info(__name__, 'data: {}', data)
    req = requests.post('http://{host}:{port}/jsonrpc'.format(host=host,
                                                              port=port),
                        data=data)
    res = req.json()
    debug.info(__name__, 'res: {}', res)
    return res

def answer():
    pass
