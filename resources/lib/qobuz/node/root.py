#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
from flag import NodeFlag as Flag
from inode import INode
from user_playlists import Node_user_playlists
from recommendation import Node_recommendation
from search import Node_search
from favorites import Node_favorites
from purchases import Node_purchases
from friend_list import Node_friend_list
from genre import Node_genre
from label import Node_label
from article_rubrics import Node_article_rubrics
import qobuz


'''
    @class Node_root:
'''


class Node_root(INode):

    def __init__(self, parent=None, parameters=None):
        super(Node_root, self).__init__(parent, parameters)
        self.type = Flag.ROOT
        self.content_type = 'files'
        self.label = "Qobuz"
        # self.image = qobuz.image.access.get('default')

    def _build_down(self, Dir, lvl, whiteFlag, blackFlag):
        self.add_child(Node_user_playlists())
        if qobuz.addon.getSetting('show_recommendations') == 'true':
            self.add_child(Node_recommendation())
        self.add_child(Node_purchases())
        self.add_child(Node_favorites())
        if qobuz.addon.getSetting('search_enabled') == 'true':
            search = Node_search()
            search.search_type = 'albums'
            self.add_child(search)
            search = Node_search()
            search.search_type = 'tracks'
            self.add_child(search)
            search = Node_search()
            search.search_type = 'artists'
            self.add_child(search)
        self.add_child(Node_friend_list())
        self.add_child(Node_genre())
        self.add_child(Node_label())
        self.add_child(Node_article_rubrics())
        return True

    def cache_remove(self):
        # ERASE CACHE
        from gui.util import yesno, notifyH, getImage
        from debug import log
        if not yesno('Remove cached data', 'Do you really want to erase all cached data'):
            log(self, "Deleting cached data aborted")
            return False
        if qobuz.registry.delete_by_name('^.*\.dat$'):
            notifyH('Qobuz cache (i8n)', 'All cached data removed')
        else:
            notifyH('Qobuz cache (i8n)',
                    'Something went wrong while erasing cached data',
                    getImage('icon-error-256'))
        return True
