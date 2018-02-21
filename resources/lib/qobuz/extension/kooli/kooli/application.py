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
import logging
from functools import wraps, update_wrapper
from datetime import datetime
from werkzeug import exceptions
from jinja2 import Undefined
from flask import Flask
from flask import request
from flask import Response, redirect
from flask import make_response, render_template, request

from qobuz.api import api
from qobuz.application import Application as QobuzApplication
from qobuz.cache import cache
from qobuz import base_path
from qobuz.plugin import Plugin
from qobuz.bootstrap import MinimalBootstrap
from qobuz.debug import logger
from qobuz.node import getNode, Flag
from qobuz.gui.directory import Directory
from qobuz import config
from qobuz.util.converter import converter
from kooli import kooli_path

qobuzApp = QobuzApplication(
    Plugin('plugin.audio.qobuz'),
    bootstrapClass=MinimalBootstrap)
qobuzApp.bootstrap.init_app()
kooli_tpl = P.join(kooli_path, 'tpl')
application = Flask(__name__, template_folder=kooli_tpl)

HEADGET = ['HEAD', 'GET']


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


_http_error = {200: 'Ok', 404: 'Not Found', 500: 'Server Error'}


def http_error(code):
    if request.method == 'HEAD':
        return '', code
    return _http_error[code], code


def shutdown_server():
    try:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        return func()
    except Exception as e:
        logger.error('shutdown server error %s', e)
    return True


@nocache
@application.route('/qobuz/ping', methods=HEADGET)
def route_ping():
    if request.method == 'HEAD':
        return '', 200
    return 'pong', 200


@nocache
@application.route('/qobuz', methods=HEADGET)
def route_root():
    response = {}
    if request.method == 'HEAD':
        return '', 200
    return render_template('root.htm.j2', **response)


@nocache
@application.route('/qobuz/<string:album_id>/<string:track_id>.mpc', methods=HEADGET)
def route_track(album_id=None, track_id=None):
    track = getNode(Flag.TRACK, parameters={'nid': track_id})
    track.data = track.fetch()
    url = track.get_streaming_url()
    if url is None:
        return http_error(404)
    return redirect(url, code=302)


@nocache
@application.route('/qobuz/<string:album_id>/fanart.jpg', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/poster.jpg', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/thumb.jpg', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/landscape.jpg', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/logo.png', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/cdart.png', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/extrafanart/', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/characterart.png', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/clearart.png', methods=HEADGET)
@application.route('/qobuz/banner.jpg', methods=HEADGET)
@application.route('/qobuz/artist.nfo', methods=HEADGET)
def route_null(album_id=None, track_id=None):
    return http_error(404)


@nocache
@application.route('/qobuz/<string:album_id>/disc.png', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/folder.jpg', methods=HEADGET)
@application.route('/qobuz/<string:album_id>/thumb.jpg', methods=HEADGET)
def route_disc_image(album_id=None, track_id=None):
    node = getNode(Flag.ALBUM, parameters={'nid': album_id})
    node.data = node.fetch()
    image = None
    if node.data is not None:
        image = node.get_image()
    if image is None:
        return http_error(404)
    return redirect(image, code=302)


@nocache
@application.route('/qobuz/<string:album_id>/album.nfo', methods=HEADGET)
def route_nfo_album(album_id=None, track_id=None):
    response = api.get('/album/get', album_id=album_id)
    if response is None:
        response = api.get('/track/get', track_id=track_id)
    if response is None:
        return http_error(404)
    response['album_id'] = album_id
    if request.method == 'HEAD':
        return '', 200
    if 'description' in response:
        response['description'] = converter.strip_html(
            response['description'], default='')
    if 'catchline' in response:
        response['catchline'] = converter.strip_html(
            response['catchline'], default='')
    response['image_default_size'] = qobuzApp.registry.get(
        'image_default_size')
    if 'duration' in response:
        response['duration'] = round(response['duration'])
    return render_template('album.nfo.j2', **response)


@nocache
@application.route('/qobuz/<string:album_id>/', methods=HEADGET)
def route_album(album_id=None, track_id=None):
    response = api.get('/album/get', album_id=album_id)
    if response is None:
        response = api.get('/track/get', track_id=track_id)
    if response is None:
        return http_error(404)
    response['album_id'] = album_id
    if request.method == 'HEAD':
        return '', 200
    if 'description' in response:
        response['description'] = converter.strip_html(
            response['description'], default='')
    if 'catchline' in response:
        response['catchline'] = converter.strip_html(
            response['catchline'], default='')
    response['image_default_size'] = qobuzApp.registry.get(
        'image_default_size')
    if 'duration' in response:
        response['duration'] = round(response['duration'])
    return render_template('dir.j2', **response)


@nocache
@application.route('/qobuz/<string:album_id>/artist.nfo', methods=HEADGET)
def route_nfo_artist(album_id=None):
    album = api.get('/album/get', album_id=album_id)
    response = None
    if album is not None:
        response = api.get('/artist/get', artist_id=album['artist']['id'])
    if response is None:
        return http_error(404)
    if 'biography' in response:
        response['biography']['content'] = converter.strip_html(
            response['biography']['content'], default='')
    response['image_default_size'] = qobuzApp.registry.get(
        'image_default_size')
    return render_template('artist.nfo.j2', **response)


@nocache
@application.route('/qobuz/favorite/', methods=HEADGET)
@application.route('/qobuz/favorite/<string:search_type>/', methods=HEADGET)
@application.route('/qobuz/favorite/<string:search_type>/<string:nid>', methods=HEADGET)
def route_favorite(search_type=None, nid=None):
    if search_type is None:
        if request.method == 'HEAD':
            return '', 200
        return render_template('favorite_index.htm.j2')
    node = getNode(
        Flag.FAVORITE, parameters={'search-type': search_type,
                                   'nid': nid})
    node.data = node.fetch()
    if node.data is None:
        return redirect('/qobuz/favorite/%s' % search_type)
    if nid is None:
        return render_template('favorite.htm.j2', **node.data)
    return render_template('%s.htm.j2' % search_type, **node.data)
