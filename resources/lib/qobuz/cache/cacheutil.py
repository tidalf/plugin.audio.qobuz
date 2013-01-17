import pickle
from util.file import FileUtil

class CacheUtil(object):

    def __init__(self):
        pass
    
    def clean_old(self, cache):
        """Callback deleting one file
        """
        def delete_one(filename, info):
            info['count'] += 1
            data = cache.load_from_store(filename)
            if cache.is_fresh(None, None, data):
                return False
            cache.delete(data['key'])
            return True
        info = {'count': 0}
        fu = FileUtil()
        fu.find(cache.cache_base_path, '^.*\.dat$', delete_one, info)
        return True
