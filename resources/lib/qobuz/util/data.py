from qobuz import debug

def list_image(data, desired_size='xlarge'):
    all_size = [desired_size]
    [all_size.append(s) for s in ['xlarge', 'large', 'small', 'thumbnail']]
    result = []
    def append(url):
        debug.info(__name__, 'appending url: {}', url)
        if url not in result:
            result.append(url)

    if data is None:
        return result
    current = data
    if 'tracks' in current:
        current = data['tracks']['items']
    for item in current:
        if 'album' in item:
            album = item['album']
            if 'image' in album:
                image = album['image']
                for size in all_size:
                    if size in image:
                        append(image[size])
                        break   
    return result
