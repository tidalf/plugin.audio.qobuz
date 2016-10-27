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
    if not is_empty(username) and not is_empty(password):
        return True
    return False

def is_service_enable():
    return gui.getSetting('enable_scan_feature', asBool=True)

@application.before_request
def shutdown_request():
    if monitor.abortRequested:
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
    alive = True
    while alive:
        abort = False
        try:
            abort = monitor.abortRequested
        except Exception as e:
            debug.error(__name__, 'Error while getting abortRequested {}', e)
        if abort:
            alive = False
            continue
        xbmc.sleep(1000)
    monitor.stop_all_service()
