import xbmc
from utils import _sc
import os
__debugging__ = 1

###############################################################################
# Loggin helper functions
###############################################################################
def log(obj,msg,lvl="LOG"):
    print(_sc('[' + lvl + '] ' + str(type(obj)) + ": " + msg))

def warn(obj,msg):
    if __debugging__:
        log(obj,msg,'WARN')

def info(obj,msg):
    if __debugging__:
        log(obj,msg,'INFO')

def error(obj,msg,code):
    log(obj,msg,'ERROR')
    os.sys.exit(code)