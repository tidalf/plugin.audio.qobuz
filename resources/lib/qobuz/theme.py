from qobuz import debug
from qobuz import config

class Theme(object):
    data = {
        'item': {
            'caution': {
                'color': config.app.registry.get('item_caution_color')
            },
            'default': {
                'color': config.app.registry.get('item_default_color')
            },
            'public': {
                'color': config.app.registry.get('item_public_color')
            },
            'private': {
                'color': config.app.registry.get('item_private_color')
            },
            'section': {
                'color': config.app.registry.get('item_section_color')
            },
            'selected': {
                'color': config.app.registry.get('item_selected_color')
            }
        },
        'menu': {
            'playlist': {
                'color': config.app.registry.get('menu_playlist_color')
            },
            'favorite': {
                'color': config.app.registry.get('menu_favorite_color')
            }
        }
    }
    _cache = {}
    def get(self, path):
        if path in self._cache:
            return self._cache[path]
        root = self.data
        for part in path.split('/'):
            if part not in root:
                raise KeyError(part)
            root = root[part]
        if root is not None:
            self._cache[path] = root
        return root

theme = Theme()
