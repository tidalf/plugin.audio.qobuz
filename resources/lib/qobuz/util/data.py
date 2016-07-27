def list_image(data, size='large'):
    result = []
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
                if size in image:
                    result.append(image[size])
                else:
                    for size in ['large', 'small', 'xlarge', 'thumbnail']:
                        if size in image:
                            result.append(image['size'])
                result.append(album['image']['thumbnail'])
    return result
