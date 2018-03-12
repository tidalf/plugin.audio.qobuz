'''
    qobuz.extension.kooli.script.kooli-xbmc-service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from os import path as P
import SocketServer
import socket
import sys
import threading
import time

base_path = P.abspath(P.dirname(__file__))
try:
    import kooli as _  # pylint:disable=E0401
except ImportError:
    sys.path.append(P.abspath(P.join(base_path, P.pardir, P.pardir)))
from kooli import qobuz_lib_path

try:
    import flask as _  # pylint:disable=E0401
except ImportError as e:
    lib_path = P.join(qobuz_lib_path,
                      'qobuz', 'extension', 'script.module.flask', 'lib')
    sys.path.append(lib_path)

from kodi_six import xbmc  # pylint:disable=E0401
from kooli.application import application, shutdown_server, qobuzApp
from kooli.monitor import Monitor
from qobuz import config
from qobuz.api import api
from qobuz.api.user import current as user
from qobuz.debug import getLogger
from qobuz.gui.util import notify_warn
import qobuz.gui.util as gui

logger = getLogger(__name__)


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
        except socket.error:
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
                        logger.error('KooliService port: %s Error: %s',
                                     self.port, e)
                        raise e
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
            logger.error('Error while getting abortRequested %s', e)
        if abort:
            alive = False
            continue
        xbmc.sleep(1000)
    monitor.stop_all_service()
