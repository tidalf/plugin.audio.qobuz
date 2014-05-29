import xbmcgui  # @UnresolvedImport


class XbmcList(xbmcgui.Window):

    def __init__(self, *a, **ka):
        self.list = None
        xbmcgui.Window(*a, **ka)

    def __import_control(self, cid):
        try:
            self.list = self.getControl(cid)
            return True
        except:
            pass
        return False

    def onInit(self):
        print "INIT"
        self.list = None
        for cid in [54]:
            if self.__import_control(cid):
                return True

    def getSelectedItem(self):
        if self.list is None:
            return None
        return self.list.getSelectedItem()

    def get_list(self):
        return self.list

    def delete(self, idx):
        if self.list is None:
            return False
        cl = self.list.copy()
        self.list.reset()
        for i in cl:
            if i == idx:
                continue
            self.list.append(cl[i])
