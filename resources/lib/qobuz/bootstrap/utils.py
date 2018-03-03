
import sys

from qobuz.debug import getLogger
from qobuz.dog import dog

logger = getLogger(__name__)


def get_checked_parameters():
    '''Parse parameters passed to xbmc plugin as sys.argv
    '''
    d = dog()
    rparam = {}
    if len(sys.argv) <= 1:
        return rparam
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        pairsofparams = cleanedparams.split('&')

        for i, _item in enumerate(pairsofparams):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                if d.kv_is_ok(splitparams[0], splitparams[1]):
                    rparam[splitparams[0]] = splitparams[1]
                else:
                    logger.warn('--- Invalid key: %s / value: %s' % (splitparams[0], splitparams[1]))
    return rparam
