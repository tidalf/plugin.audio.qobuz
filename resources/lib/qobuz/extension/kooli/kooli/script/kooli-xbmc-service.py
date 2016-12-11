'''
    qobuz.extension.kooli.script.kooli-xbmc-service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import os
from os import path as P
import time
import errno
import traceback
import threading
import requests
import SocketServer
import socket

base_path = P.abspath(P.dirname(__file__))
try:
    import kooli
except ImportError:
    sys.path.append(P.abspath(P.join(base_path, P.pardir, P.pardir)))
from kooli import log
from kooli import qobuz_lib_path
try:
    import flask
    log.info('Flask loaded from kodi addon repository')
except ImportError as e:
    log.warn('Flask not present, loading our own copy')
    path = P.join(qobuz_lib_path, 'qobuz', 'extension', 'script.module.flask',
                  'lib')
    sys.path.append(path)
from flask import request
import xbmc
from kooli.application import application, shutdown_server, qobuzApp
from kooli.monitor import Monitor
from qobuz.gui.util import notify_warn
from qobuz.api import api
import qobuz.gui.util as gui
from qobuz import config
from qobuz import debug
from qobuz.api.user import current as user


def my_finish(self):
    if not self.wfile.closed:
        try:
            self.wfile.flush()
        except socket.error:
            # A final socket error may have occurred here, such as
            # the local error ECONNABORTED.
            pass
        try:
            self.wfile.close()
            self.rfile.close()
        except socket.error as e:
            pass

SocketServer.StreamRequestHandler.finish = my_finish  # Ugly monkey patching


def is_empty(obj):
    if obj is None:
        return True
    if isinstance(obj, basestring):
        if obj == '':
            return True
    return False


def is_authentication_set():
    username = config.app.registry.get('username')
    password = config.app.registry.get('password')
    if not is_empty(username) and not is_empty(password):
        return True
    return False


def is_service_enable():
    return config.app.registry.get('enable_scan_feature', to='bool')


@application.before_request
def shutdown_request():
    if monitor.abortRequested:
        shutdown_server()
    return None


class KooliService(threading.Thread):
    name = 'httpd'

    def __init__(self, port=33574):
        threading.Thread.__init__(self)
        self.daemon = True
        self.port = port
        self.running = False
        self.threaded = True
        self.processes = 2
        self.alive = True

    def stop(self):
        shutdown_server()
        self.alive = False

    def run(self):
        while self.alive:
            if not is_authentication_set():
                gui.notify_warn('Authentication not set',
                                'You need to enter credentials')
            elif not user.logged:
                if not api.login(
                        username=qobuzApp.registry.get('username'),
                        password=qobuzApp.registry.get('password')):
                    gui.notify_warn('Login failed', 'Invalid credentials')
                else:
                    try:
                        application.run(port=self.port,
                                        threaded=True,
                                        processes=0,
                                        debug=False,
                                        use_reloader=False,
                                        use_debugger=False,
                                        use_evalex=True,
                                        passthrough_errors=False)
                    except Exception as e:
                        debug.error(self, 'KooliService port: {} Error: {}',
                                    self.port, e)
                        raise e
                        qobuzApp.plugin = None
            time.sleep(1)


if __name__ == '__main__':
    monitor = Monitor()
    if is_service_enable():
        monitor.add_service(KooliService())
    else:
        notify_warn('Qobuz service / HTTPD',
                    'Service is disabled from configuration')
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
