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
import os
import time
import platform

class Pid():

    def __init__(self, file, pid):
        self.pid = pid
        self.file = file
        self.auto_remove_old_pid = 0
        self.new_name = self.file + str(int(time.time()))
        
    def exists(self):
        if os.path.isfile(self.file):
            return True
        else: return False
    
    def set_old_pid_age(self, age):
        self.auto_remove_old_pid = int(age)
    
    def can_i_run(self):
        exists = self.exists()
        if not exists:
            return True
        if not self.auto_remove_old_pid:
            return False
        if self.age() > self.auto_remove_old_pid:
            return self.remove()
        return False
    
    def create(self):
        return self._write(os.O_WRONLY|os.O_EXCL|os.O_CREAT)
    
    def touch(self):
        return self._write(os.O_WRONLY)
    
    def _write(self, flag):
        ret = False
        fd = None
        try:
            fd = os.open(self.file, flag)
        except:
            print "Cannot open file for writing"
            return False
        with os.fdopen(fd, 'w') as fo:
            try:
                fo.write(str(self.pid))
                fo.flush()
            except:
                print "Cannot write to pid file"
                ret = False
            finally:
                ret = True
                try: os.fsync(fo)
                except:
                    print "Cannot synch pid write!"
                    ret = False
                try: fo.close()
                except:
                    print "Cannot close file!"
                    ret = False
        return ret
            

    
    def remove(self):
        print "Resolver TRY to remove pid"
        ret = False
        if not self.exists():
            print "Resolver Cannot remove existing pid\n"
            return False
        try:
            ret = os.rename(self.file, self.new_name)
        except: 
            print "Resolver Cannot rename pid file!"
            return False
        print "Resolver Try unlinking"
        retry = 3
        while retry > 0:
            os.unlink(self.new_name)
            time.sleep(1)
            if not self.exists():
                break
            retry-=1
        return not self.exists()
    
    def age(self):
        if not self.exists():
            return -1
        mtime = os.path.getmtime(self.file)
        age = time.time() - mtime
        if age > 0:
            return age
        return 0.1
    

if __name__ == "__main__":
    import time
    pid = Pid('/tmp/qobuztest.pid', os.getpid())
    if not pid.create():
        print "Cannot create pid file!"
        sys.exit(1)
    if pid.exists():
        print "Age: " + str(pid.age()) + "\n"
        time.sleep(5)
        print "Age: " + str(pid.age()) + "\n"
        pid.touch()
        print "Age: " + str(pid.age()) + "\n"
        pid.remove()
       
        
    