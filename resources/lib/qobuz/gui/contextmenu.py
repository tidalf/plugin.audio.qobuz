from exception import QobuzXbmcError as Qerror
import pprint
from gui.util import color

class _cmdType_: 
    def __init__(self):
        self.runPlugin =  1 << 1,
        self.containerUpdate =  1 << 2
cmdType = _cmdType_()
        
class contextMenu():
    def __init__(self):
        self.data = {}
        self.defaultSection = 'qobuz'
        self.colorItem = "blue"
        
    def get_section_path(self, **ka):
        path = self.defaultSection
        if 'path' in ka and ka['path']:
            path = ka['path']
        xPath = path.lower().split('/')
        section = xPath.pop(0)
        if len(xPath) == 0:
            path = None
        else:
            path = '-'.join(xPath)
#        print "Section: %s, Path: %s" % (section, path)
        return section, path
    
    def add(self, **ka):
        for key in  ['label', 'cmd']:
            if not key in ka:
                raise Qerror(who=self, 
                             what='missing_parameter', additional=key)
        if not 'cmdType' in ka:
            ka['cmdType'] = cmdType.runPlugin
        section, path = self.get_section_path(**ka)
        root = self.data
        pos = 0
        if 'pos' in ka: pos = ka['pos']
        cmd = ''
        if 'cmd' in ka: cmd = ka['cmd']
        if not section in root:
            root[section] = {
                'label': section,
                'childs': [],
                'pos': pos,
                'cmd': cmd
            }
        if not path:
            root[section]['label'] = ka['label']
            root[section]['cmd'] = cmd
            root[section]['pos'] = pos
        else:
            item = {
                    'label': ka['label'],
                    'cmd': cmd,
                    'pos': pos
                    }
            root[section]['childs'].append(item)
        return root
    
    def getTuples(self):
#        print "[Attach]"
        menuItems = []
       
        def sectionSort(key):
#            print "Key: %s" % key
            return self.data[key]['pos']
               
        def itemSort(item):
                return item['pos']        
        
        for section in sorted(self.data, key=sectionSort):
            data = self.data[section]
#            print "Section: %s / %s %s" % (section, data['label'], pprint.pformat(data))
            label = '{ %s } ' % (color(self.colorItem, data['label']))
            menuItems.append((label, data['cmd']))
            for item in sorted(data['childs'], key=itemSort):
#                print "- %s" % (item['label'])
                menuItems.append((item['label'], item['cmd']))
        return menuItems
            
if __name__ == '__main__':
    c = contextMenu()
    c.add(path='qobuz', label='Qobuz', cmd='playlist', pos = 1)
    c.add(path='playlist', label='Global', cmd='playlist', pos=2)
    c.add(path='friends', label='Global', cmd='toto', pos=3)
    c.add(path='friends/titi', label='Titi', cmd='nop', pos = 1)
    c.add(path='friends/toto', label='Toto', cmd='nop', pos = 4)
    c.add(path='friends/plop', label='Plop', cmd='nop', pos = 0)
    pprint.pprint(c.data)
    c.getTuples()
    
        