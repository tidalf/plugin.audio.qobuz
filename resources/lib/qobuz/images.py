import os
        
class QobuzImages():

    def __init__(self, base_path):
        self.base_path = base_path
    
    def get(self, name, path = '', ext = 'png'):
        path = os.path.join(self.base_path, path, name + '.' + ext)
        #print "Path: " + path + "\n"
        return path
    
    def genre(self, name):
        if isinstance(name, int):
            if name == 0:
                name = 'default'
            elif name == 64:
                name = 'electro'
            elif name == 80:
                name = 'jazz'
        return self.get(name, 'genres')