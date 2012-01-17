import sys
import os
import time
import platform

class Pid():

    def __init__(self, file, pid):
        self.pid = pid
        self.file = file
        self.auto_remove_old_pid = 0
        
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
        except: 
            print "Cannot rename pid file "
            return False
        os.unlink(newname)
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
       
        
    