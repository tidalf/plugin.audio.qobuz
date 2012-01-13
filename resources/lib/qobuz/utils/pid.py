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
        if not os.write(fd, str(self.pid)):
            os.close(fd)
            return False
        os.close(fd)
        return True
    
    def touch(self):
        if not self.exists():
            return False
        fd = os.open(self.file, os.O_WRONLY)
        if not fd:
            return False
        if not os.write(fd, str(self.pid)):
            os.close(fd)
            return False
        os.close(fd)
        return True
    
    def remove(self):
        if not self.exists():
            return False
        os.unlink(self.file)
        try:
            name = platform.system()
            print "Platform: " + name
            if name == 'Windows':
                time.sleep(1)
        except: pass
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
       
        
    