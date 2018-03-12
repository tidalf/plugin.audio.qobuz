'''
    qobuz
    ~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from os import path as P

from qobuz.config import *

base_path = P.abspath(P.join(P.dirname(__file__), P.pardir))
data_path = P.join(base_path, 'qobuz', '__data__')
