'''
    console
    ~~~~~~~

    Qobuz console
    
    ::Note: Under windows you need to install pyreadline...
    
    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import code
try:
    import readline
except:
    import pyreadline as readline

import atexit
import os
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.cache import cache
from node.renderer.list import ListRenderer
from node import url2dict
from qobuz.settings import settings
import random

VERSION='0.0.1'

class _c:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    GREEN = '\033[92m'

def color(type, msg):
    return '%s%s%s' % (type, msg, _c.ENDC)

class QobuzConsole(code.InteractiveConsole):

    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser("~/.console-history")):

        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)
        self.last_prompt = None
        self.no_display = False
        self.env = None
        self.env_stack = []
        self.write_history = False
        rlist = ListRenderer()
        rlist.whiteFlag = Flag.ALL
        rlist.blackFlag = Flag.NONE
        self.renderer = rlist
        self.alive = True
        self.available_commands = ['view', 'back', 'help', 'quit', 'fuzz']
        self._cmd_stack = [] #[('view', [0])] 

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        if not self.write_history:
            return
        readline.write_history_file(histfile)

    def start(self):
        while self.alive:
            try:
                self.process()
            except KeyboardInterrupt:
                self.command_quit(None)
            except Exception as e:
                import traceback
                print "Error %e" % (e)
                traceback.print_stack()
                raise e

    def process(self):
        kind = self.env['kind'] if (self.env and 'kind' in self.env) else None
        flag = kind or Flag.ROOT
        node = getNode(flag, self.env or {})
        node.populating(self.renderer)
        self.last_prompt = node.get_label()
        self.display(self.renderer)
        if len(self._cmd_stack) > 0:
            cmd = self._cmd_stack.pop(0)
            if self.exec_command(cmd):
                self.write('\n>> command: %s, Ok <<\n' % (cmd[0]))
                self.write('\tPrevious: %s\n' % (node.get_label()))
            else:
                self.write('\n>> command %s, error <<\n' % (cmd[0]))
        else:
            #self._cmd_stack.append(('fuzz', []))
            self._cmd_stack.append(self.get_command())
        return True 

    def get_prompt(self, label=None):
        prompt = label or self.last_prompt
        if prompt and len(prompt) > 40:
            prompt = '%s...' % (prompt[0:40]) 
        return '>>> %s: ' % (prompt.encode('ascii', 'ignore') or 'Qobuz')

    def get_command(self):
        inp = self.raw_input(self.get_prompt())
        inpx = inp.split(' ')
        if inpx[0] in self.available_commands:
            return (inpx[0], inpx[1:])
        return None

    def exec_command(self, tuple):
        if tuple is None:
            return True
        name, args = tuple
#        try:
        return getattr(self, 'command_%s' % (name))(args)
#        except Exception as e:
#            self.write('>>> Invalid command %s (%s)\n\t%s\n' % (name, 
#                                                                args, e))
        return False

    def display(self, nlist):
        if self.no_display:
            self.no_display = False
            return
        count = 0
        msg = '\n'
        for node in nlist:
            method = 'display_%s' % (Flag.to_s(node.kind))
            imsg = ''
            if hasattr(self, method):
                imsg = '[%s] %s' % (count, getattr(self, method)(node))
            else:
                imsg = '[%s] %s\n' % (count, node.get_label())
            msg+=imsg
            count += 1
        self.write(msg)

    def display_track(self, node):
        msg = '%s (%2.2f mn)\n' % (node.get_title(), node.get_duration()/60.0)
        info=''
        pkind = node.parent.kind if node.parent else None
        if pkind and not (pkind & Flag.PLAYLIST == Flag.PLAYLIST):
            info = '\t%s - %s\n' % (node.get_artist(), 
                                             node.get_album())
            if len(info) >= 80:
                info = info[0:79] + '\n'
            msg = color(_c.GREEN, msg)
        return '%s%s' % (msg, info) 

    def command_view(self, args):
        node = None
        try:
            idx = int(args[0])
            node = self.renderer[idx]
        except Exception as e:
            self.write('>>>> Invalid index: %s\n' % (e))
            return False
        if self.env:
            self.env_stack.append(self.env.copy())
        else:
            self.env_stack.append({'kind': Flag.ROOT})
        self.env = url2dict(node.url())
        self.renderer.clear()
        self.renderer.depth = 1
        method = 'command_view_%s' % (Flag.to_s(node.kind))
        if hasattr(self, method):
            return getattr(self, method)(node)
        return True

    def command_view_track(self, node):
        return self.command_back(None)

    def command_fuzz(self, args):
        size = len(self.renderer)
        if size == 0 or random.randint(0,9) > 5:
            return self.command_back(args)
        idx = random.randint(0, size-1)
        if self.renderer[idx].kind & Flag.TRACK:
            return self.command_back(args)
        return self.command_view([idx])

    def command_quit(self, args):
        self.alive = False
        self.write('\n>> quit...\n')

    def command_back(self, args):
        try:
            if len(self.env_stack) == 0:
                self.env = None
            else:
                self.env = self.env_stack.pop()
            self.renderer.clear()
            self.renderer.depth = 1
            return True
        except Exception as e:
            self.write('Cannot go back: %s\n' % (e))
        return False

    def command_help(self, args):
        msg = '::Qobuz console (%s)\n' % (VERSION)
        msg+= '\t:: view <idx>\n\t\tenter directory with index idx\n'
        msg+= '\t:: back\n\t\tback to parent\n'
        msg+= '\t:: quit\n\t\tquit interactive console\n'
        msg+= '\t:: help\n\t\tthis help\n'
        self.no_display = True
        self.write(msg)
        return True

'''Main
'''
import tempfile
__tempdir__ = tempfile.gettempdir()
__tempdir__ = os.path.join(__tempdir__, 'qobuzcache')
if not os.path.exists(__tempdir__):
    if not os.path.exists(__tempdir__):
        os.mkdir(__tempdir__)
        if not os.path.exists(__tempdir__):
            print "Cannot make temporary directory: %s" % (__tempdir__)
            __tempdir__ = None
if __tempdir__:
    cache.base_path = __tempdir__
c = QobuzConsole()
c.write('>> Qobuz console(%s)\n' % (VERSION))
#settings['search_enable'] = False
try:
    while not api.is_logged:
        username = c.raw_input(c.get_prompt('Login'))
        password = c.raw_input(c.get_prompt('Password'))
        api.login(username, password)
    c.write('Logged as %s\n' % (api.username))
    c.start()
except KeyboardInterrupt as e:
    pass
finally:
    print ">> cleaning"
    api.logout()
    cache.delete_all()
    if os.path.exists(__tempdir__):
        os.rmdir(__tempdir__)
    print "Bye :)"