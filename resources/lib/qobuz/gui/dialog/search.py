import sys
import xbmcgui, xbmc

#getLocalizedString = sys.modules['__main__'].getLocalizedString

class Dialog(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

    def onInit(self):
        #blanks the screen - this is crude, and probably wrong, but works
        self.background = xbmcgui.ControlImage(0,0,1280,720, 'black.png')
        self.addControl(self.background)
        self.action_exitkeys_id = [10, 13]
        self.keyboard = xbmc.Keyboard()
        self.addControl(self.keyboard)
        
        # get control ids
#        self.control_id_button_action = 3000
#        self.control_id_button_exit = 3001
#        self.control_id_label_action = 3011
        
        # translation ids
#        self.translation_id_action = 3101
#        self.translation_id_exit = 3102
#        self.translation_id_demotext = 3120
        
        # set actions
#        self.button_action = self.getControl(self.control_id_button_action)
#        self.button_exit = self.getControl(self.control_id_button_exit)
        
        # translate buttons
#        self.button_action.setLabel(getLocalizedString(self.translation_id_action))
#        self.button_exit.setLabel(getLocalizedString(self.translation_id_exit))

    def onAction(self, action):
        if action in self.action_exitkeys_id:
            self.closeDialog()

    def onFocus(self, controlId):
        pass

    def onClick(self, controlId):
        pass
#        if controlId == self.control_id_button_action:
#            self.doAction()
#        elif controlId == self.control_id_button_exit:
#            self.closeDialog()

    def doAction(self):
        pass

    def closeDialog(self):
        self.close()