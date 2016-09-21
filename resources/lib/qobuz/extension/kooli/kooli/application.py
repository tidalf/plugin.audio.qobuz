import os
from os import path as P
from flask import Flask
from flask import request
from qobuz.api import api
from qobuz.application import Application as QobuzApplication
from qobuz.cache import cache
from flask import Response, redirect
from qobuz import base_path
from qobuz.plugin import Plugin
from qobuz.bootstrap import MinimalBootstrap
from qobuz.debug import info, warn, error
qobuzApp = QobuzApplication(Plugin('plugin.audio.qobuz'),
                            bootstrapClass=MinimalBootstrap)
qobuzApp.bootstrap.init_app()
info(None, 'Username %s Password %s' % (qobuzApp.registry.get('username'),
                                   qobuzApp.registry.get('password')))
api.login(username=qobuzApp.registry.get('username'),
          password=qobuzApp.registry.get('password'))


application = Flask(__name__)

from qobuz.gui.util import getSetting
from werkzeug import exceptions
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)

def http_error(name):
    return getattr(exceptions, name)()

def get_format_id(default=3):
    stream_type = getSetting('streamtype')
    if stream_type == 'flac':
        return 5
    elif stream_type == 'mp3':
        return 3
    return default

def shutdown_server():
    info(__name__, 'Shutting down server')
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@nocache
@application.route('/qobuz/track/<int:track_id>.mpc', methods=['HEAD'])
def route_track_head(track_id=None):
    response = api.get('/track/getFileUrl',
                       format_id=get_format_id(),
                       track_id=track_id)
    if response is None or 'url' not in response:
        return http_error('NotFound')
    return 'ok', 200

@nocache
@application.route('/qobuz/track/<int:track_id>.mpc', methods=['GET'])
def route_track(track_id=None):
    response = api.get('/track/getFileUrl',
                       format_id=get_format_id(),
                       track_id=track_id)
    if response is None or 'url' not in response:
        return http_error('NotFound')
    return redirect(response['url'])

@application.route('/<path:path>')
def sniff(path=None):
    info(__name__, 'Request[{}] {}', request.method, path)
    return http_error('NotFound')
