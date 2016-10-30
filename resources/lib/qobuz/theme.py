from qobuz import debug
from qobuz.gui.util import getSetting

class Theme(object):
    data = {
        'item': {
            'caution': {
                'color': getSetting('item_caution_color')
            },
            'default': {
                'color': getSetting('item_default_color')
            },
            'public': {
                'color': getSetting('item_public_color')
            },
            'private': {
                'color': getSetting('item_private_color')
            },
            'section': {
                'color': getSetting('item_section_color')
            },
            'selected': {
                'color': getSetting('item_selected_color')
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
