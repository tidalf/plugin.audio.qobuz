'''
    qobuz
    ~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from os import path as P
base_path = P.abspath(P.join(P.dirname(__file__), P.pardir))
data_path = P.join(base_path, 'qobuz', '__data__')
