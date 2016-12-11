'''
    qobuz.extension.kooli.application
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
from os import path as P
import pprint
from functools import wraps, update_wrapper
from datetime import datetime
from werkzeug import exceptions
from jinja2 import Undefined
from flask import Flask
from flask import request
from flask import Response, redirect
JINJA2_ENVIRONMENT_OPTIONS = {'undefined': Undefined}
from flask import make_response, render_template, request

from qobuz.api import api
from qobuz.application import Application as QobuzApplication
from qobuz.cache import cache
from qobuz import base_path
from qobuz.plugin import Plugin
from qobuz.bootstrap import MinimalBootstrap
from qobuz import debug
from qobuz.node import getNode, Flag
from qobuz.gui.directory import Directory
from qobuz import config
from kooli import kooli_path

qobuzApp = QobuzApplication(
    Plugin('plugin.audio.qobuz'), bootstrapClass=MinimalBootstrap)
qobuzApp.bootstrap.init_app()
kooli_tpl = P.join(kooli_path, 'tpl')
application = Flask(__name__, template_folder=kooli_tpl)


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers[
            'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


def http_error(name):
    return 'error', 500


def shutdown_server():
    try:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        return func()
    except Exception as e:
        debug.error(__name__, 'shutdown server error {}', e)
    return True


@nocache
@application.route('/qobuz/ping', methods=['HEAD', 'GET'])
def route_ping():
    if request.method == 'HEAD':
        return '', 200
    return 'pong', 200


@nocache
@application.route('/qobuz', methods=['HEAD', 'GET'])
def route_root():
    response = {}
    if request.method == 'HEAD':
        return '', 200
    return render_template('root.htm.tpl', **response)


@nocache
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/file.mpc',
    methods=['GET', 'HEAD'])
def route_track(album_id=None, track_id=None):
    track = getNode(Flag.TRACK, parameters={'nid': track_id})
    track.data = track.fetch()
    url = track.get_streaming_url()
    if url is None:
        if request.method == 'HEAD':
            return '', 200
        return 'Not Found', 404
    return redirect(url, code=302)


@nocache
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/extrafanart/',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/cdart.png',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/channellogo.png',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/characterart.png',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/clearart.png',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/logo.png',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/landscape.jpg',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/banner.jpg',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/poster.jpg',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/fanart.jpg',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/fanart.jpg', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/poster.jpg', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/thumb.jpg', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/landscape.jpg', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/logo.png', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/cdart.png', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/extrafanart/', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/characterart.png', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/clearart.png', methods=['GET', 'HEAD'])
@application.route('/qobuz/banner.jpg', methods=['GET', 'HEAD'])
@application.route('/qobuz/artist.nfo', methods=['GET', 'HEAD'])
def route_null(album_id=None, track_id=None):
    if request.method == 'HEAD':
        return '', 404
    return 'Not Found', 404


@nocache
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/disc.png',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/disc.png', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/folder.jpg',
    methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/folder.jpg', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/<string:album_id>/thumb.jpg', methods=['GET', 'HEAD'])
def route_disc_image(album_id=None, track_id=None):
    node = getNode(Flag.ALBUM, parameters={'nid': album_id})
    node.data = node.fetch()
    image = None
    if node.data is not None:
        image = node.get_image()
    if image is None:
        if request.method == 'HEAD':
            return '', 404
        return 'Not Found', 404
    return redirect(image, code=302)


@nocache
@application.route(
    '/qobuz/<string:album_id>/<string:track_id>/album.nfo',
    methods=['GET', 'HEAD'])
def route_nfo_album(album_id=None, track_id=None):
    response = api.get('/album/get', album_id=album_id)
    if response is None:
        response = api.get('/track/get', track_id=track_id)
    if response is None:
        if request.method == 'HEAD':
            return '', 404
        return 'NotFound', 404
    if response['description'] is None:
        response['description'] = ''
    response['image_default_size'] = qobuzApp.registry.get(
        'image_default_size')
    if 'duration' in response:
        response['duration'] = round(response['duration'])
    return render_template('album.nfo.tpl', **response)


@nocache
@application.route(
    '/qobuz/<string:album_id>/artist.nfo', methods=['GET', 'HEAD'])
def route_nfo_artist(album_id=None):
    album = api.get('/album/get', album_id=album_id)
    response = None
    if album is not None:
        response = api.get('/artist/get', artist_id=album['artist']['id'])
    if response is None:
        if request.method == 'HEAD':
            return '', 404
        else:
            return 'NotFound', 404
    response['image_default_size'] = qobuzApp.registry.get(
        'image_default_size')
    return render_template('artist.nfo.tpl', **response)


@nocache
@application.route('/qobuz/favorite/', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/favorite/<string:search_type>/', methods=['GET', 'HEAD'])
@application.route(
    '/qobuz/favorite/<string:search_type>/<string:nid>',
    methods=['GET', 'HEAD'])
def route_favorite(search_type=None, nid=None):
    if search_type is None:
        if request.method == 'HEAD':
            return '', 200
        return render_template('favorite_index.htm.tpl')
    node = getNode(
        Flag.FAVORITE, parameters={'search-type': search_type,
                                   'nid': nid})
    node.data = node.fetch()
    if node.data is None:
        return redirect('/qobuz/favorite/%s' % search_type)
    if nid is None:
        return render_template('favorite.htm.tpl', **node.data)
    return render_template('%s.htm.tpl' % search_type, **node.data)
