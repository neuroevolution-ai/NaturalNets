class Cache:
    cache: str = ''

    def get_cache() -> str:
        return Cache.cache
    
    def set_cache(newCache: str) -> None:
        Cache.cache = newCache