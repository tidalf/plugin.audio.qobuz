'''
    console
    ~~~~~~~

    Qobuz console

    ::dependencies::
        requests
        pyreadline (win)
        colorama (win)

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import code
try:
    import readline  # @UnusedImport
except:
    import pyreadline as readline  # @UnresolvedImport @Reimport
import atexit
import os
import sys
from qobuz.api import api
from qobuz.node import getNode, Flag
from qobuz.cache import cache
from node.renderer.list import ListRenderer
from node import url2dict
from qobuz.settings import settings
import random

VERSION = '0.0.1'
DEBUG = False

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
WHITE = '\033[47;30m'
RED = '\033[41;30m'
IRED = '\033[41;30m'
GREEN = '\033[42m'
ENDC = '\033[0m'


def _c(kind, msg):
    return msg
#    return '%s%s%s' % (kind, msg, ENDC)

sep_info = _c(GREEN, '::')
sep_cmd = _c(RED, '>>>')
sep_res = _c(GREEN, '>>>')
sep_error = _c(RED, '   @#! >>>')


def sep_count(idx):
    return '%s%s%s' % (_c(RED, '['), idx, _c(RED, ']'))


class QobuzConsole(code.InteractiveConsole):

    def __init__(self, locals=None, filename="<console>",  # @ReservedAssignment
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
        self.available_commands = ['view', 'back', 'help', 'quit', 'fuzz',
                                   'set', 'home', 'action']
        self._cmd_stack = [  # ('view', [2]),
                           # ('view', [0]),
                           ('action', ['cache_delete_old'])]

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

    def yesno(self, question):
        res = ''
        import re
        m = None
        pat = re.compile('^(y(es)?|n(o)?)$',)
        while not m:
            res = self.raw_input('%s (yes/no): ' % question)
            m = pat.search(res)
        if m.group(0).startswith('y'):
            return True
        return False

    def start(self):
        while self.alive:
#            try:
                self.process()
#            except KeyboardInterrupt:
#                self.command_quit(None)
#            except Exception as e:
#                import traceback
#                print " >>> Error %s" % (e)
#                traceback.print_stack()
#                raise e

    def process(self):
        kind = self.env['kind'] if (self.env and 'kind' in self.env) else None
        flag = kind or Flag.ROOT
        node = getNode(flag, self.env or {})
        self.node = node
        node.populating(self.renderer)
        self.last_prompt = node.get_label()
        self.display(self.renderer)
        if len(self._cmd_stack) > 0:
            cmd = self._cmd_stack.pop(0)
            if not self.exec_command(cmd):
                self.write('\n%s command %s Error\n' % (sep_error, cmd[0]))
        else:
            # self._cmd_stack.append(('fuzz', []))
            self._cmd_stack.append(self.get_command())
        return True

    def get_prompt(self, label=None):
        prompt = label or self.last_prompt
        if prompt and len(prompt) > 40:
            prompt = '%s...' % (prompt[0:40])
        return '#> %s: ' % (prompt.encode('ascii', 'ignore') or 'Qobuz')

    def get_command(self):
        inp = self.raw_input(self.get_prompt())
        if not inp:
            return (None, None)
        inpx = inp.split(' ')
        if inpx[0] in self.available_commands:
            return (inpx[0], inpx[1:])
        return (None, None)

    def exec_command(self, t):
        if t is None:
            return True
        name, args = t
        if name is None:
            return True
#        try:
        return getattr(self, 'command_%s' % (name))(args)
#        except Exception as e:
#            self.write('%s Invalid command %s (%s)\n\t%s\n' % (sep_error, name,
#                                                                args, e))
        return False

    def display(self, nlist):
        if self.no_display:
            self.no_display = False
            return
        count = 0
        msg = '::[ %s ]\n' % (Flag.to_s(self.node.kind))
        ma = ''
        if self.node:
            for action in self.node.actions:
                target = ''
                if 'target' in self.node.actions[action]:
                    target = Flag.to_s(self.node.actions[action]['target'])
                ma += '%s/%s ' % (target, action)
        if ma:
            ma = '::[ %s ]' % ma
        msg += ma + '\n' + '-' * 79 + '\n'
        for node in nlist:
            method = 'display_%s' % (Flag.to_s(node.kind))
            imsg = ''
            if hasattr(self, method):
                imsg = '%s %s' % (sep_count(count), getattr(self, method)(node))
            else:
                imsg = '%s %s\n' % (sep_count(count), node.get_label())
            msg += imsg
            count += 1
        msg += '\n'
        self.write(msg)

    def display_track(self, node):
        msg = '%s - %s (%2.2f mn)\n' % (node.get_artist(),
                                        node.get_title(),
                                        node.get_duration() / 60.0)
        return msg

    def command_view(self, args):
        node = None
        try:
            idx = int(args[0])
            node = self.renderer[idx]
        except Exception as e:
            self.write(' >>> Invalid index: %s\n' % (e))
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
        if size == 0 or random.randint(0, 9) > 5:
            return self.command_back(args)
        idx = random.randint(0, size - 1)
        if self.renderer[idx].kind & Flag.TRACK:
            return self.command_back(args)
        return self.command_view([idx])

    def command_quit(self, args):
        self.alive = False
        self.write('\n:: quit\n')
        return True

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
            self.write(' >>> Cannot go back: %s\n' % (e))
        return False

    def command_set(self, args):
        self.no_display = True
        if not args or len(args) < 2:
            self.write(':: Settings:\n')
            for k in settings:
                self.write(' - %s: %s\n' % (k, settings[k]))
            return True
        try:
            key, value = args
            settings[key] = value
            self.write(' > set %s = %s' % (key, value))
            return True
        except Exception as e:
            self.write('Cannot set << %s >> with value << %s >>\n\t%s\n' % (key, value, e))
        return False

    def exec_action(self, node, action):
        a = node.actions[action]
        self.no_display = True
        target = node
        if 'target' in a and a['target'] is not None:
            tmp = target
            target = getNode(a['target'], node.parameters)
            node = tmp
        meth = 'action_%s_%s' % (Flag.to_s(target.kind), action)
        if not hasattr(self, meth):
            print "error ... %s" % meth
            raise NotImplementedError(meth)
        getattr(self, meth)(node, target)

    def command_action(self, args):
        if self.node is None:
            print "No current node, cannot execute action"
            return False
        request = args[0]
        for action in self.node.actions:
            if action == request:
                self.exec_action(self.node, action)
                return True
        return False

    def action_favorite_add_tracks(self, source, target):
        tracks = target.list_tracks(source)
        print "[ Favorite / Add tracks ]"
        for track in tracks:
            print ' - %s' % track.get_label()
        if not self.yesno('Add %s tracks to favorite ?' % len(tracks)):
            return False
        track_ids = ','.join([str(track.nid) for track in tracks])
        if target.add_tracks(track_ids):
            print "%s track(s) added to favorite" % (len(tracks))
            return True
        print "Cannot add tracks to favorite"
        return True

    def action_root_cache_delete_old(self, source, target):
        res = source.cache_delete_old()
        if res > 0:
            print "%s file(s) deleted from cache" % res
        return True

    def action_root_cache_delete_all(self, source, target):
        res = source.cache_delete_all()
        if res > 0:
            print "%s file(s) deleted from cache" % res
        return True

    def command_help(self, args):
        msg = '::Qobuz console (%s)\n' % (VERSION)
        msg += '\t:: view <idx>\n\t\tenter directory with index idx\n'
        msg += '\t:: back\n\t\tback to parent\n'
        msg += '\t:: action <name>\n\t\tExecute action on current node\n'
        msg += '\t:: quit\n\t\tquit interactive console\n'
        msg += '\t:: set <key> <value>\n\t\t setting key to value\n'
        msg += '\t:: home\n\t\tgo root\n'
        msg += '\t:: help\n\t\tthis help\n'
        self.no_display = True
        self.write(msg)
        return True

    def command_home(self, args):
        self.env = None
        self.env_stack = []
        self.renderer.clear()
        self.renderer.depth = 1
        return True


def hasargv(name):
    for arg in sys.argv[1:]:
        print "ARG %s %s" % (name, arg)
        if name == arg:
            return True
    return False
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
# api.login('', '')
if not DEBUG and api.password:
    raise Exception('Password disclosure!')
# settings['search_enable'] = False
# settings['recommendation_enabel'] = False

c = QobuzConsole()
c.write_history = True
c.write('%s qobuz console (%s)\n' % (sep_info , VERSION))
try:
    while not api.is_logged:
        username = c.raw_input(c.get_prompt('Login'))
        password = c.raw_input(c.get_prompt('Password'))
        if not api.login(username, password):
            c.write(api.error)
    c.write('%s Logged as %s\n' % (sep_res, api.username))
    c.start()
except KeyboardInterrupt as e:
    pass
finally:
    c.write(":: cleaning\n")
    count = cache.delete_old()
    c.write(" > cache cleaned: %s file(s)\n" % (count))
    c.write(":: bye :)\n")
