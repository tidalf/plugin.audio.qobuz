import sys
import os
import time
import platform

class Pid():

    def __init__(self, file, pid):
        self.pid = pid
        self.file = file
        
    def exists(self):
        if os.path.isfile(self.file):
            return True
        else: return False
    
    def create(self):
        if self.exists():
            return False
        fd = os.open(self.file, os.O_WRONLY|os.O_EXCL|os.O_CREAT)
        if not fd:
            return False
        try:
            os.write(fd, str(self.pid))
        finally:
            #f.flush()
            os.fsync(fd)
            os.close(fd)
        return True
    
    def touch(self):
        if not self.exists():
            return False
        try:
            fd = os.open(self.file, os.O_WRONLY)
        except: return False
        if not fd:
            return False
        try:
            os.write(fd, str(self.pid))
        finally:
            #f.flush()
            os.fsync(fd)
            os.close(fd)
        return True
    
    def remove(self):
        if not self.exists():
            return False
        newname = self.file + str(int(time.time()))
        print "New name: " + newname
        try:
            os.rename(self.file, newname)
        except: return False
        #self.file = newname
        os.unlink(newname)
#        try:
#            name = platform.system()
#            print "Platform: " + name
#            if name == 'Windows':
#                timeout = 10
#                while timeout > 0:
#                    if not self.exists():
#                        return True
#                    timeout-=1
#                    time.sleep(1)
#        except: pass
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
    pid = Pid('C:/Users/sho/AppData/Roaming/XBMC/cache/temp/qobuztest.pid', os.getpid())
    if not pid.create():
        print "Cannot create pid file!"
        #sys.exit(1)
    if pid.exists():
        print "Age: " + str(pid.age()) + "\n"
        time.sleep(5)
        print "Age: " + str(pid.age()) + "\n"
        pid.touch()
        print "Age: " + str(pid.age()) + "\n"
        pid.remove()
       
        
    