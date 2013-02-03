import code
try:
    import readline
except:
    import pyreadline as readline
    
import atexit
import os

class HistoryConsole(code.InteractiveConsole):

    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser("~/.console-history")):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)
    
    def get_command(self):
        inp = self.raw_input("\n#> ")
        inpx = inp.split(' ')
        if inpx[0].startswith('view'):
            return ('view', int(inpx[1]))
        return ('nop', None)
            
console = HistoryConsole()