'''
    qobuz.dog
    ~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import re

_allowed_keys = {
    'mode': r'^\d{1,10}$',  # Mode View/Scan/BigDir ...
    'nid':  r'^\d{1,14}$',  # Node id (node.nid)
    'nt':   r'^\d{1,10}$',  # Node type (node.type)
    'qnt':  r'^\d{1,20}$',  # Node type in query
    'qid':  r'^\d{1,14}$',  # Node id in query
    'purchased': r'^\d{1,10}$',
    'nm': r'^[\w\d_]+$',    # Method to be called on node
    'genre-type': r'^(\d+|null)$',  # Reco params
    'genre-id': r'^(\d+|null)$',    # Reco params
    'search-type': r'^(artists|tracks|albums|articles|all)$',
    'depth': r'^(-)?\d+$',
    'query': r'^.*$',
    'track-id': r'^\d{1,10}$',
    'parent-id': r'^\d{1,10}$',
    'offset': r'^\d{1,10}$',
    'source': r'^(all|playlists|purchases|favorites)$',

}
_allowed_boolean = ['asLocalUrl']

_allowed_keys = {key: re.compile(value) for key, value in _allowed_keys.items()}

class dog():
    '''Checking script parameter against regular expression
    '''

    def __init__(self):
        pass

    def kv_is_ok(self, key, value):
        if key in _allowed_boolean:
            if value not in ['True', 'False']:
                return False
            return True
        if key not in _allowed_keys:
            return False
        if _allowed_keys[key].match(value) is None:
            return False
        return True
