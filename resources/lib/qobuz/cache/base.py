from time import time
__version__ = "0.0.1"
__author__ = "d@corp/cache/%s" % (__version__)
__magic__ = 0
for i in [ord(c) for c in __author__[:]]:
    __magic__ += i

BadMagic = 1 << 1
BadKey = 1 << 2
NoData = 1 << 3
StoreError = 1 << 4
DeleteError = 1 << 5

class CacheBaseDecorator(object):
    ''' A base decorator class, This is for caching function that
    have form func(path, parameters = { 'type'="foo", 'has_audio'=False }
    '''
    def __init__(self, *a, **ka):
        pass

    def cached(self, f, *a, **ka):
        that = self
        def wrapped_f(self, *a, **ka):
            that.error = 0
            key = that.make_key(self, *a, **ka)
            data = that.retrieve(self, key, *a, **ka)
            if data:
                if not that.check_magic(self, data, *a, **ka):
                    that.error &= BadMagic
                elif not that.check_key(self, data, key, *a, **ka):
                    that.error &= BadKey
                elif that.is_fresh(self, key, data, *a, **ka):
                    print "Is FRESH :]"
                    return data['data']
                if not that.delete(self, key):
                    that.error = DeleteError
            data = f(self, *a, **ka)
            if data is None:
                that.error &= NoData
                return None
            if 'password' in ka:
                ka['password'] = '***'
            entry = {
                 'updated_on': time(),
                 'data': data,
                 'ttl': that.get_ttl(self, key, *a, **ka),
                 'pa': a,
                 'ka': ka,
                 'magic': __magic__,
                 'key': key
            }
            if not that.store(self, key, entry):
                that.error &= StoreError
            return data
        return wrapped_f

    def is_fresh(self, obj, key, data, *a, **ka):
        if not 'updated_on' in data:
            return False
        updated_on = data['updated_on']
        ttl = data['ttl']
        diff = (updated_on + ttl) - time()
        if diff < 0:
            return False
        return True

    def check_magic(self, obj, data, *a, **ka):
        if not 'magic' in data:
            return False
        if data['magic'] != __magic__:
            return False
        return True

    def check_key(self, obj, data, key, *a, **ka):
        if not 'key' in data:
            return False
        if data['key'] != key:
            return False
        return True

    def retrieve(self, obj, key, *a, **ka):
        ''' return tuple (Status, Data)
            Status: Bool
            Data: Arbitrary data
        '''
        raise NotImplemented()
    
    def load_from_store(self, *a, **ka):
        raise NotImplemented()
    
    def store(self, obj, key, data, *a, **ka):
        raise NotImplemented()

    def delete(self, obj, key, *a, **ka):
        raise NotImplemented()

    def make_key(self, obj, key, *a, **ka):
        raise NotImplemented()

    def get_ttl(self, obj, key, *a, **ka):
        raise NotImplemented
