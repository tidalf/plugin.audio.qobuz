
def make_local_track_url(config, track):
    return '{scheme}://{host}:{port}/qobuz/{album_id}/{nid}.mpc'.format(
            scheme='http',
            host=config.app.registry.get('httpd_host'),
            port=config.app.registry.get('httpd_port'),
            album_id=track.get_album_id(),
            nid=str(track.nid))

def make_local_album_url(config, album):
    return '{scheme}://{host}:{port}/qobuz/{album_id}/'.format(
            scheme='http',
            host=config.app.registry.get('httpd_host'),
            port=config.app.registry.get('httpd_port'),
            album_id=album.nid)