class __NodeFlag():
    def __init__(self): 
        self.DONTFETCHTRACK = 1
        self.TYPE_NODE = 512
        self.TYPE_TRACK = 1024
        self.TYPE_PLAYLIST = 2048
        self.TYPE_USERPLAYLISTS = 4096

NodeFlag = __NodeFlag()