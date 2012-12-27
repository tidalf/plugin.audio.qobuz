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

import xbmc
import qobuz

'''
    Keyboard
'''
class Keyboard(xbmc.Keyboard):
    
    def __init__(self, default, heading, hidden = True):
        self.setHeading('Qobuz / ' + heading)
        
'''
    Notify Human
'''
def notifyH(title, text, image = None, mstime = 2000):
    try: 
        if not image: image = qobuz.image.access.get('qobuzIcon')
    except: pass
    s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (title, text, mstime, image)
    xbmc.executebuiltin(s.encode('utf-8', 'replace'))

'''
    Notify
'''
def notify(title, text, image = None, mstime = 2000):
    #if not image: image = qobuz.image.access.get('qobuzIcon')
    l = qobuz.lang
    s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (l(title), l(text), mstime, image)
    xbmc.executebuiltin(s.encode('utf-8', 'replace'))