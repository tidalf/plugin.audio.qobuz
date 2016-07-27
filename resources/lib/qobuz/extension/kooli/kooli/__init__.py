import sys
import os
from os import path as P
import logging

logging.basicConfig()
log = logging.getLogger('kooli')
log.setLevel(logging.DEBUG)
base_path = P.abspath(P.join(P.dirname(__file__), P.pardir))
qobuz_lib_path = P.abspath(P.join(base_path, P.pardir, P.pardir, P.pardir))
sys.path.append(qobuz_lib_path)

if __name__ == '__main__':
    log.info('koooli')
    log.info('\nbase_path: %s\nqobuz_lib_path: %s', base_path, qobuz_lib_path)
    from qobuz.api import api
    log.info(dir(api))
