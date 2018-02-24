import sys
from os import path as P

qobuzPath = P.abspath(P.join(P.dirname(__file__), P.pardir))
sys.path.append(qobuzPath)