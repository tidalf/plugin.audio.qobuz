'''
    qobuz.util.data
    ~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''


def list_image(data, desired_size='xlarge'):
    all_size = [desired_size]
    _ = [all_size.append(s) for s in ['xlarge', 'large', 'small', 'thumbnail']]
    result = []

    def append(url):
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
