import cmd
import sys
from qobuz.application import Application
from qobuz.bootstrap.shell import ShellBootstrap
from qobuz.plugin.shell import ShellPlugin
from qobuz.debug import getLogger
logger = getLogger(__name__)


class QobuzShell(cmd.Cmd):
    intro = 'Welcome to the qobuz shell.   Type help or ? to list commands.\n'
    prompt = '(qobuz) '
    file = None

    def __init__(self, *a, **ka):
        self.application = Application(
            bootstrapClass=ShellBootstrap, plugin=ShellPlugin)
        cmd.Cmd.__init__(self, *a, **ka)

    def do_dumpconf(self, arg):
        for section, key, value in self.application.registry:
            logger.info('[%s] %s: %s', section, key, value)


def loop():
    QobuzShell().cmdloop()
