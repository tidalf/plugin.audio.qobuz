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
from qobuz import debug
from kooli import kooli_path
qobuzApp = QobuzApplication(Plugin('plugin.audio.qobuz'),
                            bootstrapClass=MinimalBootstrap)
qobuzApp.bootstrap.init_app()
kooli_tpl = P.join(kooli_path, 'tpl')
application = Flask(__name__, template_folder=kooli_tpl)

from werkzeug import exceptions
from flask import make_response, render_template, request
from functools import wraps, update_wrapper
from datetime import datetime
from qobuz.node import getNode, Flag
from qobuz.gui.directory import Directory
from qobuz import config

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
    return 'error', 500
    #return getattr(exceptions, name)()

def get_format_id(default=3):
    stream_type = config.app.registry.get('streamtype')
    if stream_type == 'flac':
        return 6
    elif stream_type == 'mp3':
        return 5
    return default

def shutdown_server():
    try:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        return func()
    except Exception as e:
        debug.error(__name__, 'shutdown server error {}', e)
    return False


@nocache
@application.route('/qobuz/ping', methods=['HEAD', 'GET'])
def route_ping():
    return 'pong', 200

@nocache
@application.route('/qobuz', methods=['HEAD', 'GET'])
def route_root():
    node = getNode(Flag.ROOT)
    directory = Directory(node)
    node.populating(directory)
    response = {
        'childs': [{'label': c.label} for c in node.childs],
    }
    return render_template('root.tpl', **response)

@nocache
@application.route('/qobuz/<string:album_id>/<string:track_id>/file.mpc', methods=['HEAD'])
def route_track_head(album_id=None, track_id=None):
    hires = config.app.registry.get('hires_enabled', to='bool')
    if hires and self.get_hires():
        format_id = 27
    else: 
        format_id = get_format_id()
    if (self.get_property('purchased') or self.get_parameter('purchased') == '1' or self.purchased) and hires:
       intent = "download"
    else:
       intent = "stream"
    response = api.get('/track/getFileUrl',
                    format_id=format_id,
                    track_id=track_id,
                    intent=intent)
    if response is None or 'url' not in response:
        return 'NotFound', 404 #http_error('NotFound')
    return 'ok', 200


@nocache
@application.route('/qobuz/<string:album_id>/<string:track_id>/file.mpc', methods=['GET'])
def route_track(album_id=None, track_id=None):
    response = api.get('/track/getFileUrl',
                       format_id=get_format_id(),
                       track_id=track_id)
    if response is None or 'url' not in response:
        return 'NotFound', 404#http_error('NotFound')
    return redirect(response['url'], code=302)


@nocache
@application.route('/qobuz/<string:album_id>/<string:track_id>/album.nfo', methods=['GET', 'HEAD'])
def route_nfo_album(album_id=None, track_id=None):
    response = api.get('/album/get', album_id=album_id)
    if response is None:
        response = api.get('/track/get', track_id=track_id)
        if response is None:
            return 'NotFound', 404 #http_error('NotFound')
    if request.method == 'HEAD':
        return 'ok', 200
    if not response['description']:
        response['description'] = ''
    response['image_default_size'] = qobuzApp.registry.get('image_default_size')
    if 'duration' in response:
        response['duration'] = round(response['duration'])
    debug.info(__name__, 'ALBUMNFO {}', response)
    return render_template('album.nfo.tpl', **response)



@nocache
@application.route('/qobuz/<string:album_id>/artist.nfo', methods=['GET', 'HEAD'])
def route_nfo_artist(album_id=None):
    album = api.get('/album/get', album_id=album_id)
    if album is None:
        return 'NotFound', 404#http_error('NotFound')
    response = api.get('/artist/get', artist_id=album['artist']['id'])
    if response is None:
        return 'NotFound', 404 #http_error('NotFound')
    if request.method == 'HEAD':
        return 'ok', 200
    debug.info(__name__, 'ARTISTNFO {}', response)
    response['image_default_size'] = qobuzApp.registry.get('image_default_size')
    return render_template('artist.nfo.tpl', **response)
