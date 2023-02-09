class Cache:
    cache: str = ''

    def getCache():
        return Cache.cache
    
    def setCache(newCache: str):
        Cache.cache = newCache