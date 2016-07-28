import os
from os import path as P
from flask import Flask
from flask import request
from kooli import log
from qobuz.api import api
from qobuz.application import Application as QobuzApplication
from qobuz.cache import cache
from flask import Response, redirect
from qobuz import base_path
from qobuz.plugin import Plugin
from qobuz.bootstrap import MinimalBootstrap
qobuzApp = QobuzApplication(Plugin('plugin.audio.qobuz'), bootstrapClass=MinimalBootstrap)
cache_path = P.join(base_path, '__data__', 'cache')
qobuzApp.bootstrap.cache = cache_path
cache.base_path = qobuzApp.bootstrap.cache
if not P.exists(qobuzApp.bootstrap.cache):
    os.makedirs(qobuzApp.bootstrap.cache)
api.login(username=qobuzApp.registry.get('username'),
          password=qobuzApp.registry.get('password'))

application = Flask(__name__)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@application.route('/qobuz/<int:user_id>/<int:album_id>/<int:track_id>.mpc', methods=['GET'])
def route_track(user_id=None, album_id=None, track_id=None):
    response = api.get('/track/getFileUrl', format_id=3, track_id=track_id)
    if response is None or 'url' not in response:
        return 'NoFound', 404
    return redirect(response['url'])

@application.route('/<path:query>')
def sniff(path=None):
    log.info('Request[%s] %s', request.method, path)
    return 'File Not Found', 404
