'''
    qobuz.alarm
    ~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import time

from qobuz.gui import util


class Repeatable(object):
    def __init__(self, callback=lambda elpased: None, duration=1):
        self.duration = duration
        self.updated = None
        self.callback = callback
        self.last = None
        self.start()

    def start(self):
        self.last = time.time()

    def check(self):
        now = time.time()
        elapsed = now - self.last
        if elapsed > self.duration:
            self.last = now
            return self.callback(elapsed)
        return None


class Notifier(Repeatable):
    class Item(object):
        def __init__(self, text, level='info'):
            self.text = text.encode('ascii', errors='ignore')
            self.level = level

        def __str__(self):
            return '[%s] %s' % (self.level, self.text)

    def __init__(self, title='Notifier', duration=5, _callback=None):
        super(Notifier, self).__init__(
            duration=duration, callback=self._callback)
        self.store = []
        self.title = title
        self.total = 0

    def _callback(self, _elapsed):
        msg = u', '.join([str(n.text) for n in self.store])
        msg = msg[:-2]
        visited = len(self.store)
        self.total += visited
        self.store = []
        if hasattr(self.title, '__call__'):
            title = self.title()
        else:
            title = self.title
        util.notify_log(
            '%s nodes: %s' % (title, self.total),
            '%s' % msg,
            mstime=self.duration * 1000)
        return True

    def notify(self, text, level='info', check=False):
        self.store.append(Notifier.Item(text, level=level))
        if check is True:
            self.check()
