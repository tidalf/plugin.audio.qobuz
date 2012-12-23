import sys
import pprint
import traceback
class QobuzXbmcError(Exception):
    def __init__(self, *args, **kwargs):
        if (not 'who' in kwargs) or (not 'what' in kwargs): 
            raise Exception('QobuzXbmcError', 'Missing constructor arguments (who|what)')
        msg = 'QobuzXbmcError: '  + pprint.pformat(kwargs)
        print msg
        traceback.print_stack()
        print repr(traceback.extract_stack())
        print repr(traceback.format_stack())
        raise self
#        sys.exit(1)