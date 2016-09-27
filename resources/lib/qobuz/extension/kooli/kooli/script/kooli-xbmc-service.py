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

from kooli import qobuz_lib_path
path = P.join(qobuz_lib_path, 'qobuz', 'extension', 'script.module.flask', 'lib')
sys.path.append(path)

from kooli.application import application, shutdown_server, qobuzApp
from kooli import log
from kooli.monitor import Monitor
import xbmc
from qobuz.gui.util import getSetting, notify_warn
from qobuz.api import api
import qobuz.gui.util as gui
from qobuz import debug
from flask import request
import traceback
import threading

def is_empty(obj):
    if obj is None:
        return True
    if isinstance(obj, basestring):
        if obj == '':
            return True
    return False

def is_authentication_set():
    username = gui.getSetting('username')
    password = gui.getSetting('password')
    debug.info(__name__, 'username: {}, password: {}', username,
               '***' if password else 'None')
    if not is_empty(username) and not is_empty(password):
        return True
    return False

def is_service_enable():
    return gui.getSetting('enable_httpd_service', asBool=True)

@application.before_request
def shutdown_request():
    debug.info(__name__, 'request: {}', request.url)
    if monitor.abortRequested:
        debug.info(__name__, 'Shutdown Qobuz Httpd requested')
        shutdown_server()
    return None

class KooliService(threading.Thread):
    name = 'httpd'
    def __init__(self, port=33574):
        threading.Thread.__init__(self)
        self.port = port
        self.running = False
        self.threaded = True
        self.processes = 2
        self.alive = True

    def stop(self):
        self.alive = False
        shutdown_server()

    def run(self):
        while self.alive:
            if not is_authentication_set():
                gui.notify_warn('Authentication not set', 'You need to enter credentials')
            elif not api.is_logged:
                if not api.login(username=qobuzApp.registry.get('username'),
                    password=qobuzApp.registry.get('password')):
                    gui.notify_warn('Login failed', 'Invalid credentials')
                else:
                    try:
                        debug.info(self, 'Starting {} on port {}', self.name, self.port)
                        application.run(port=self.port, threaded=True)
                    except Exception as e:
                        debug.error(self, 'KooliService port: {} Error: {}', self.port, e)
            xbmc.sleep(1000)


if __name__ == '__main__':
    if not is_service_enable():
        notify_warn('Qobuz service / HTTPD', 'Service is disabled from configuration')
        sys.exit(0)
    monitor = Monitor()
    monitor.add_service(KooliService())
    monitor.start_all_service()
    #debug.info(__name__, 'Listening on http://localhost: {}', monitor.service['httpd'].service.port)
    alive = True
    while alive:
        abort = False
        try:
            abort = monitor.abortRequested
        except Exception as e:
            debug.error(__name__, 'Error while getting abortRequested {}', e)
        if abort:
            debug.info(__name__, 'Abort!')
            alive = False
            continue
        xbmc.sleep(1000)
    #     try:
    #         if not is_authentication_set():
    #             gui.notify_warn('Authentication not set', 'You need to enter credentials')
    #             xbmc.sleep(5000)
    #             continue
    #         if not api.login(username=qobuzApp.registry.get('username'),
    #             password=qobuzApp.registry.get('password')):
    #             gui.notify_warn('Login failed', 'Invalid credentials')
    #             xbmc.sleep(5000)
    #             continue
    #         debug.info(__name__, '--> starting Flask')
    #         application.run(port=port, threaded=True)
    #         while True:
    #             xbmc.sleep(1000)
    #     except Exception as e:
    #         debug.error(__name__, '>>>[-] Flask failed...Error {}', e)
    #         traceback.print_exc(file=sys.stdout)
    #         print '-'*60
    #         xbmc.sleep(1000)
    monitor.stop_all_service()
    debug.info(__name__, 'Qobuz/Kooli ended!')
