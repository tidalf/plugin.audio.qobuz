#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
import sys
import pprint
import traceback

class QobuzXbmcError(Exception):
    
    def __init__(self, *a, **ka):
        if not 'additional' in ka or ka['additional'] == None: ka['additional'] = ''
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
