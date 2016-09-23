import sys
import os
from os import path as P
import time
import requests
import errno
base_path = P.abspath(P.dirname(__file__))
try:
  import kooli
except ImportError:
    sys.path.append(P.abspath(P.join(base_path, P.pardir, P.pardir)))

#try:
#    import flask
#except Exception:
from kooli import qobuz_lib_path
path = P.join(qobuz_lib_path, 'qobuz', 'extension', 'script.module.flask', 'lib')
sys.path.append(path)

from kooli.application import application, shutdown_server
from kooli import log
import xbmc
from qobuz.gui.util import getSetting, notify_warn
from qobuz import debug
from flask import request

if __name__ == '__main__':
    enable = getSetting('enable_httpd_service', asBool=True)
    if enable is False:
        notify_warn('Qobuz service / HTTPD', 'Service is disabled from configuration')
        sys.exit(0)
    monitor = xbmc.Monitor()
    port = 33574
    @application.before_request
    def shutdown_request():
        debug.info(__name__, 'request: {}', request.url)
        if monitor.abortRequested():
            #shutdown = True
            debug.info(__name__, 'Shutdown Qobuz Httpd requested')
            #shutdown_server()
        return None

    debug.info(__name__, 'Qobuz HTTP Service http://localhost:{}', port)
    while True:
        try:
            debug.info(__name__, '--> starting Flask')
            application.run(port=port, threaded=True)
            debug.info(__name__, '<-- stopping Flask')
            #xbmc.sleep(1)
        except Exception as e:
            debug.error(__name__, '>>>[-] Flask failed...Error {}', e)
    debug.info(__name__, 'MONITOR END Bye!')
