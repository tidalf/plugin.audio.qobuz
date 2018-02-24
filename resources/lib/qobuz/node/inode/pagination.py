_paginated = [
    'albums', 'labels', 'tracks', 'artists', 'playlists', 'playlist',
    'public_playlists', 'genres'
]


def addint(*a):
    return sum(int(s) for s in a)


def add_pagination(node, data):
    '''build_down helper: Add pagination data when needed
    '''
    if not data:
        return False
    items = None
    for kind in _paginated:
        if kind in data and data[kind]:
            items = data[kind]
            break
    if items is None:
        return False
    if 'limit' not in items or 'total' not in items:
        return False
    if items['limit'] is None:
        return False
    newlimit = addint(items['offset'], items['limit'])
    if items['total'] < newlimit:
        return False
    url = node.make_url(offset=newlimit)
    node.pagination_next = url
    node.pagination_total = items['total']
    node.pagination_offset = items['offset']
    node.pagination_limit = items['limit']
    node.pagination_next_offset = newlimit
    return True
