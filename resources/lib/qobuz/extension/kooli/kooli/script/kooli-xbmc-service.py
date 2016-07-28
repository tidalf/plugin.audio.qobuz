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

try:
    import flask
except ImportError:
    from kooli import qobuz_lib_path
    path = P.join(qobuz_lib_path, 'qobuz', 'extension', 'script.module.flask', 'lib')
    sys.path.append(path)

from kooli.application import application, shutdown_server
from kooli import log
import xbmc
from qobuz.gui.util import getSetting, notify_warn
from qobuz.debug import error, info

if __name__ == '__main__':
    enable = getSetting('enable_httpd_service', asBool=True)
    if enable is False:
        notify_warn('Qobuz service / HTTPD', 'Service is disabled from configuration')
        sys.exit(0)
    monitor = xbmc.Monitor()
    port = 33574

    @application.before_request
    def shutdown_request():
        if monitor.abortRequested():
            shutdown_server()

    info(__name__, 'Starting Qobuz HTTP Service http://localhost:{}', port)
    while not monitor.abortRequested():
        try:
            application.run(port=port)
        except Exception as e:
            error(__name__, 'Error {}', e)
            xbmc.sleep(3)

    info(__name__, 'Bye!')
