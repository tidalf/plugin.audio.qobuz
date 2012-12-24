import sys
import pprint
import traceback

class QobuzXbmcError(Exception):
    
    def __init__(self, *a, **ka):
        nl = "\n"
        if (not 'who' in ka) or (not 'what' in ka): 
            raise Exception('QobuzXbmcError', 'Missing constructor arguments (who|what)')
        msg = "[QobuzXbmcError]" + nl
        msg+= " - who        : " + pprint.pformat(ka['who']) + nl
        msg+= " - what       : " + ka['what'] + nl
        msg+= " - additional : " + ka['additional'] + nl
        msg+= " - Stack      : " + nl
        print msg
        traceback.print_stack()
