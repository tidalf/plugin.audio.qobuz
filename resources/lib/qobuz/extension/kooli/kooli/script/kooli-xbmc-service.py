import sys
import os
from os import path as P
import time
import requests
base_path = P.abspath(P.dirname(__file__))
try:
  import kooli
except ImportError:
  sys.path.append(P.abspath(P.join(base_path, P.pardir, P.pardir)))
from kooli.application import application, shutdown_server
from kooli import log
import xbmc


if __name__ == '__main__':
    monitor = xbmc.Monitor()
    port = 33574
    @application.before_request
    def shutdown_request():
        global monitor
        if monitor.abortRequested():
            shutdown_server()

    while not monitor.abortRequested():
        log.info('Starting Qobuz HTTP Service on port: %s', port)
        try:
            application.run(port=port)
        except Exception as e:
            log.error('Error %s', e)
    log.info('Bye!')
