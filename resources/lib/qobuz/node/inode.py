'''
    qobuz.node.inode
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from node import BaseNode

class INode(BaseNode):
    def __init__(self, parameters = {}):
        self.data = None
        super(INode, self).__init__(parameters)
        self.content_type = "files"
        self.pagination_next = None
        self.pagination_prev = None
        self.user_storage = None
        
    def populating(self, renderer=None):
        if self.get_property('total'):
            print "Has pagination..."
        return super(INode, self).populating(renderer)

#    def __add_pagination(self, data):
#        """build_down helper: Add pagination data when needed
#        """
#        if not data:
#            return False
#        paginated = ['albums', 'labels', 'tracks', 'artists',
#                     'playlists', 'playlist']
#        items = None
#        need_pagination = False
#        for p in paginated:
#            if p in data:
#                items = data[p]
#                if items['limit'] is None:
#                    continue
#                if items['total'] > (items['offset'] + items['limit']):
#                    need_pagination = True
#                    break
#        if not need_pagination:
#            return False
#        url = self.make_url(offset=items['offset'] + items['limit'])
#        self.pagination_next = url
#        self.pagination_total = items['total']
#        self.pagination_offset = items['offset']
#        self.pagination_limit = items['limit']
#        self.pagination_next_offset = items['offset'] + items['limit']

    '''
        Parameters
        A hash for storing script parameter, each node have a copy of them.
        TODO: each node don't need to copy parameter
    '''
#    def set_parameters(self, parameters):
#        """Setting parameters property
#            Parameter:
#                parameters: Dictionary
#        """
#        self.parameters = parameters
#
#    def set_parameter(self, name, value, **ka):
#        """Setting a parameter
#            Parameters:
#                name: parameter name
#                value: parameter value
#            
#            * Optional quote=True/False, when quote=True we are using
#            urllib.quote_plus befoer setting value
#        """
#        if 'quote' in ka and ka['quote'] == True:
#            value = urllib.quote_plus(value)
#        self.parameters[name] = value

#    def get_parameter(self, name, **ka):
#        if not self.parameters:
#            return None
#        if not name in self.parameters:
#            return None
#        if 'unQuote' in ka and ka['unQuote'] == True:
#            return urllib.unquote_plus(self.parameters[name])
#        return self.parameters[name]

#    def del_parameter(self, name):
#        if not name in self.parameters:
#            return False
#        del self.parameters[name]
#        return True

#    def make_url(self, **ka):
#        '''Generate URL to navigate between nodes
#            Nodes with custom parameters must override this method
#            @todo: Ugly need rewrite =]
#        '''
#        if not 'mode' in ka:
#            ka['mode'] = Mode.VIEW
#        else:
#            ka['mode'] = int(ka['mode'])
#        if not 'nt' in ka:
#            ka['nt'] = self.nt
#        if not 'nid' in ka and self.nid:
#            ka['nid'] = self.nid
#     
#        url = sys.argv[0] + '?mode=' + str(ka['mode']) + '&nt=' + \
#            str(ka['nt'])
#        if 'nid' in ka:
#            url += "&nid=" + str(ka['nid'])
#        offset = self.offset
#        if 'offset' in ka: offset = ka['offset']
#        if offset != None:
#            url += '&offset=' + str(offset)
#        if 'nm' in ka:
#            url += '&nm=' + ka['nm']
#        qnt = self.get_parameter('qnt')
#        if 'qnt' in ka:
#            qnt = ka['qnt']
#        if qnt:
#            url+= '&qnt=' + str(qnt)
#        qid = self.get_parameter('qid')
#        if 'qid' in ka:
#            qid = ka['qid']
#        if qid:
#            url+= '&qid=' + str(qid)
#        if 'query' in ka:
#            url+= '&query=' + ka['query']
#        return url

#    '''
#        Make Xbmc List Item
#        return  a xbml list item
#        Class can overload this method
#    '''
#    def makeListItem(self, **ka):
#        import xbmcgui
#        if not 'url' in ka:
#            ka['url'] = self.make_url()
#        if not 'label' in ka:
#            ka['label'] = self.get_label()
#        if not 'label2' in ka:
#            ka['label2'] = self.get_label()
#        if not 'image' in ka:
#            ka['image'] = self.get_image()
#        item = xbmcgui.ListItem(
#            ka['label'],
#            ka['label2'],
#            ka['image'],
#            ka['image'],
#            ka['url']
#        )
#        ctxMenu = contextMenu()
#        self.attach_context_menu(item, ctxMenu)
#        item.addContextMenuItems(ctxMenu.getTuples(), ka['replaceItems'])
#        item.addContextMenuItems(ctxMenu.getTuples(), ka['replaceItems'])
#        return item

#    def add_child(self, child):
#        child.parent = self
#        child.set_parameters(self.parameters)
#        self.childs.append(child)
#        return self

#    def get_childs(self):
#        return self.childs

#    def set_label(self, label):
#        self.label = label #label.encode('utf8', 'replace')
#        return self
#
#    def get_image(self):
#        if self.image:
#            return self.image
#        if self.parent:
#            return self.parent.get_image()
#        return self.get_property('image')
#
#    def set_image(self, image):
#        self.image = image
#        return self
#
#    def get_label(self):
#        return self.label
#
#    def get_label2(self):
#        return self.label2
#
#    def render_nodes(self, nt, parameters, lvl = 1, whiteFlag = Flag.ALL, 
#                     blackFlag = Flag.TRACK & Flag.STOPBUILD):
#        render = renderer(nt, parameters)
#        render.depth = -1
#        render.whiteFlag = whiteFlag
#        render.blackFlag = blackFlag
#        render.asList = True
#        render.run()
#        return render

    # When returning False we are not displaying directory content
#    def fetch(self, Dir, lvl=1, whiteFlag=None, blackFlag=None):
#        '''This method fetch data from cache
#        '''
#        return True

#    def populating(self, Dir, lvl=1, whiteFlag=None, blackFlag=None, 
#                   gData=None):
#        if Dir.Progress.iscanceled():
#            return False
#        if not gData:
#            gData = {'count': 0,
#                     'total': 100,
#                     'startedOn': time()}
#        if lvl != -1 and lvl < 1:
#            return False
#        Dir.update(gData, 'Fetching', '', '')
#        if not (self.nt & blackFlag == self.nt):
#            if not self.fetch(Dir, lvl, whiteFlag, blackFlag):
#                return False
#            else:
#                self.__add_pagination(self.data)
#        self.populate(Dir, lvl, whiteFlag, blackFlag)
#        """ Recursive mode dont't decrement level """
#        if lvl != -1:
#            lvl -= 1
#        label = self.get_label()
#        gData['count'] = 0
#        gData['total'] = len(self.childs)
#        self.__add_pagination_node(Dir, lvl, whiteFlag)
#        Dir.update(gData, 'Working', label, '')
#        for child in self.childs:
#            if Dir.is_canceled():
#                return False
#            """ Only white Flagged added to the listing """
#            if child.nt & whiteFlag == child.nt:
#                if not Dir.add_node(child):
#                    warn(self, "Something went wrong... aborting")
#                    self.childs = []
#                    raise Qerror(who=self, what='build_down_abort')
#                gData['count'] += 1
#                Dir.update(gData, "Working", label, child.get_label())
#            else:
#                log(self, "Skipping node: %s" % ( Flag.to_s(child.nt)) )
#            """ Calling builiding down on child """
#            child.populating(Dir, lvl, whiteFlag, blackFlag, gData)
#        return gData['count']

#    def populate(self, xbmc_directory, lvl, Flag):
#        """Hook/_build_down:
#        This method is called by build_down, each object who
#        inherit from Inode can overide it. Lot of object
#        simply fetch data from qobuz (cached data)
#        """
#        pass
    
#    def __add_pagination_node(self, Dir, lvl=1, whiteFlag=Flag.NODE):
#        """Helper/Called by build_down to add special node when pagination is
#        required
#        """
#        if self.pagination_next:
#            colorItem = getSetting('color_item')
#            params = qobuz.boot.params
#            params['offset'] = self.pagination_next_offset
#            params['nid'] = self.nid
#            node = getNode(self.nt, params)
#            node.data = self.data
#            label = self.get_label()
#            if not label and self.parent:
#                label = self.parent.get_label()
#            if self.label2: label = self.label2
#            nextLabel = (
#                '[ %s  %s / %s ]') % (color(colorItem, label),
#                                      self.pagination_next_offset,
#                                      self.pagination_total)
#            node.label = nextLabel
#            node.label2 = label
#            self.add_child(node)

#    def attach_context_menu(self, item, menu):
#        """
#            Note: Url made with make_url must set mode (like mode=Mode.VIEW)
#            else we are copying current mode (for track it's Mode.PLAY ...)
#        """
#        ''' HOME '''
#        colorCaution = getSetting('item_caution_color')
#
#        url = self.make_url(nt=Flag.ROOT, mode=Mode.VIEW, nm='')
#        menu.add(path='qobuz', label="Qobuz", cmd=containerUpdate(url, False),
#                 id='', pos = -5)     
#        ''' ARTIST '''
#        if self.nt & (Flag.ALBUM | Flag.TRACK | Flag.ARTIST):
#            artist_id = self.get_artist_id()
#            #if not artist_id:
#            #    import pprint
#            #    print pprint.pformat(self.data)
#            artist_name = self.get_artist()
#            urlArtist = self.make_url(nt=Flag.ARTIST, nid=artist_id, 
#                                      mode=Mode.VIEW)
#            menu.add(path='artist/all_album', 
#                          label="%s %s" % (lang(39001), artist_name), 
#                          cmd=containerUpdate(urlArtist), pos=-10)
#
#            ''' Similar artist '''
#            url = self.make_url(nt=Flag.SIMILAR_ARTIST, 
#                                nid=artist_id, mode=Mode.VIEW)
#            menu.add(path='artist/similar', 
#                          label=lang(39004), 
#                          cmd=containerUpdate(url))
#        ''' FAVORITES '''
#        wf = self.nt & (~Flag.FAVORITES)
#        if self.parent:
#            wf = wf and self.parent.nt & ~Flag.FAVORITES
#        if wf:
#            ''' ADD TO FAVORITES / TRACKS'''
#            url = self.make_url(nt=Flag.FAVORITES,
#                                nm='', mode=Mode.VIEW)
#            menu.add(path='favorites', label="Favorites", 
#                     cmd=containerUpdate(url, True),pos=-9)   
#            url = self.make_url(nt=Flag.FAVORITES, 
#                                          nm='gui_add_tracks', 
#                                          qid=self.nid, 
#                                          qnt=self.nt, 
#                                          mode=Mode.VIEW)
#            menu.add(path='favorites/add_tracks', 
#                          label=lang(39011) + ' tracks', cmd=runPlugin(url))
#            ''' ADD TO FAVORITES / Albums'''
#            url = self.make_url(nt=Flag.FAVORITES, 
#                                          nm='gui_add_albums', 
#                                          qid=self.nid, 
#                                          qnt=self.nt, 
#                                          mode=Mode.VIEW)
#            menu.add(path='favorites/add_albums', 
#                          label=lang(39011) + ' albums', cmd=runPlugin(url))
#            ''' ADD TO FAVORITES / Artists'''
#            url = self.make_url(nt=Flag.FAVORITES, 
#                                          nm='gui_add_artists', 
#                                          qid=self.nid, 
#                                          qnt=self.nt, 
#                                          mode=Mode.VIEW)
#            menu.add(path='favorites/add_artists', 
#                          label=lang(39011) + ' artists', cmd=runPlugin(url))
#
#        if self.parent and (self.parent.nt & Flag.FAVORITES):
#            url = self.make_url(nt=Flag.FAVORITES,
#                                nm='', mode=Mode.VIEW)
#            menu.add(path='favorites', label="Favorites", 
#                     cmd=containerUpdate(url, True),pos=-9)  
#            url = self.make_url(nt=Flag.FAVORITES, nm='gui_remove',
#                                qid=self.nid, qnt=self.nt,
#                                mode=Mode.VIEW)
#            menu.add(path='favorites/remove', 
#                     label='Remove %s' % (self.get_label()), 
#                     cmd=runPlugin(url), color=colorCaution)
#        wf = ~Flag.USERPLAYLISTS
##        if self.parent:
##            wf = wf and self.parent.nt & (~Flag.USERPLAYLISTS)
#        if wf: 
#            ''' PLAYLIST '''
#            cmd = containerUpdate(self.make_url(nt=Flag.USERPLAYLISTS, 
#                                    nid='', mode=Mode.VIEW))
#            menu.add(path='playlist', pos = 1,
#                          label="Playlist", cmd=cmd, mode=Mode.VIEW)
#
#            ''' ADD TO CURRENT PLAYLIST '''
#            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST, 
#                                            nm='gui_add_to_current', 
#                                            qnt=self.nt,
#                                            mode=Mode.VIEW,
#                                            qid=self.nid))
#            menu.add(path='playlist/add_to_current', 
#                          label=lang(39005), cmd=cmd)
#            label = self.get_label()
#            try:
#                label = label.encode('utf8', 'replace')
#            except:
#                warn(self, "Cannot set query..." + repr(label))
#                label = ''
#            label = urllib.quote_plus(label)
#            ''' ADD AS NEW '''
#            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST,
#                                            nm='gui_add_as_new', 
#                                            qnt=self.nt,
#                                            query=label,
#                                            mode=Mode.VIEW,
#                                            qid=self.nid))
#            menu.add(path='playlist/add_as_new', 
#                          label=lang(30080), cmd=cmd)
#
##            ''' Show playlist '''
##            if not (self.nt ^ Flag.USERPLAYLISTS != Flag.USERPLAYLISTS):
##                cmd = containerUpdate(self.make_url(nt=Flag.USERPLAYLISTS, 
##                                    id='', mode=Mode.VIEW))
##                menu.add(path='playlist/show', 
##                          label=lang(39006), cmd=cmd)
#
#        ''' PLAYLIST / CREATE '''
#        cFlag = (Flag.PLAYLIST | Flag.USERPLAYLISTS)
#        if self.nt | cFlag == cFlag:
#            cmd = runPlugin(self.make_url(nt=Flag.PLAYLIST, 
#                                          nm="gui_create", mode=Mode.VIEW))
#            menu.add(path='playlist/create', 
#                          label=lang(39008), cmd=cmd)
#        ''' VIEW BIG DIR '''
#        cmd = containerUpdate(self.make_url(mode=Mode.VIEW_BIG_DIR))
#        menu.add(path='qobuz/big_dir', 
#                          label=lang(39002), cmd=cmd)
#        ''' SCAN '''
#        if getSetting('enable_scan_feature', isBool=True):
#            query = urllib.quote_plus(self.make_url(mode=Mode.SCAN))
#            url = self.make_url(nt=Flag.ROOT, mode=Mode.VIEW,
#                                nm='gui_scan', query=query)
#            menu.add(path='qobuz/scan', 
#                            cmd=runPlugin(url),
#                            label='scan')
#        if self.nt & (Flag.ALL & ~Flag.ALBUM & ~Flag.TRACK 
#                        & ~Flag.PLAYLIST):
#            ''' ERASE CACHE '''
#            cmd = runPlugin(self.make_url(nt=Flag.ROOT, nm="cache_remove", 
#                                      mode=Mode.VIEW))
#            menu.add(path='qobuz/erase_cache', 
#                          label=lang(31009), cmd=cmd, 
#                          color=colorCaution, pos=10)
#
#    def get_user_storage(self):
#        if self.user_storage:
#            return self.user_storage
#        filename = os.path.join(cache.base_path, 'localuserdata-%s.local' %
#                            str(api.user_id))
#        self.user_storage = _Storage(filename)
#        return self.user_storage
#
#    def get_user_data(self):
#        data = api.get('/user/login', username=api.username, 
#                       password=api.password)
#        if not data: 
#            return None
#        return data['user']
