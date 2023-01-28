class Cache:
    cache: str = ''

    def getCache(self):
        return self.cache
    
    def setCache(self, newCache: str):
        self.cache = newCache