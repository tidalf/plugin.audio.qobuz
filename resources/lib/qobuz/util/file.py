'''
    qobuz.util.file
    ~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import re
import tempfile

from qobuz.debug import getLogger
from qobuz.util.common import Struct

logger = getLogger(__name__)


def unlink(filename):
    logger.info('unlink %s', filename)
    if not os.path.exists(filename):
        logger.warn('InvalidUnlinkPath %s', filename)
        return False
    _, tmpfile = tempfile.mkstemp(
        u'.dat', u'invalid-', os.path.dirname(filename))
    try:
        os.rename(filename, tmpfile)
        os.unlink(tmpfile)
        return True
    except Exception as e:
        logger.error('Unlinking fails: %s, error: %s', filename, e)
    return False


class RenamedTemporaryFile(object):
    """A temporary file object which will be renamed to the specified
    path on exit.

    From http://stackoverflow.com/
        questions/12003805/threadsafe-and-fault-tolerant-file-writes
    """

    def __init__(self, final_path, **kwargs):
        tmpfile_dir = kwargs.pop('dir', None)

        # Put temporary file in the same directory as the location for the
        # final file so that an atomic move into place can occur.

        if tmpfile_dir is None:
            tmpfile_dir = os.path.dirname(final_path)

        self.tmpfile = tempfile.NamedTemporaryFile(
            dir=tmpfile_dir, delete=False, **kwargs)
        self.final_path = final_path

    def __getattr__(self, attr):
        """Delegate attribute access to the underlying temporary file object.
        """
        return getattr(self.tmpfile, attr)

    def __enter__(self):
        self.tmpfile.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.tmpfile.delete = False
            result = self.tmpfile.__exit__(exc_type, exc_val, exc_tb)
            os.rename(self.tmpfile.name, self.final_path)
        else:
            self.tmpfile.delete = True
            result = self.tmpfile.__exit__(exc_type, exc_val, exc_tb)
            os.unlink(self.tmpfile.name)
        return result


def _find_walk(path):
    for dirname, _dirnames, filenames in os.walk(path):
        for filename in filenames:
            yield Struct(**{
                'filename': filename,
                'full_path': os.path.join(dirname, filename)
            })


def _find_callback(callback, file_info):
    if callback is None:
        return True
    return callback(file_info.full_path)


def find(root_path, pattern, callback=None):
    flist = []
    pattern_ok = re.compile(pattern)
    for file_info in _find_walk(root_path):
        if pattern_ok.match(file_info.filename):
            _find_callback(callback, file_info)
            flist.append(file_info.full_path)
    return flist
