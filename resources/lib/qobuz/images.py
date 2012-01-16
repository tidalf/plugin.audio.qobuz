import os
        
class QobuzImages():

    def __init__(self, base_path):
        self.base_path = base_path
        self.images = {}
        self.add('fanArt',    os.path.join(base_path, '..', '..',  'fanart.jpg'))
        self.add('qobuzIcon', os.path.join(base_path, 'default.png'))
        self.add('qobuzIconRed', os.path.join(base_path, 'default_red.png'))
        
    def add(self, name, filename):
        print 'Add image %s: %s\n' % (name, filename)
        self.images[name] = filename
        
    def get(self, name, path = '', ext = 'png'):
        if name in self.images:
            return self.images[name]
        path = os.path.join(self.base_path, path, name + '.' + ext)
        self.add(name, path)
        return path
    
    def genre(self, name):
        if isinstance(name, int):
            if name == 0:
                name = 'default'
            elif name == 64:
                name = 'electro'
            elif name == 80:
                name = 'jazz'
        return self.get('genre.name', 'genres')
    
    def getFanArt(self):
        return self.fanArt