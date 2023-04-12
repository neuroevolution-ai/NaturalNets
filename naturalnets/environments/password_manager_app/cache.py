class Cache:
    cache: str = ""

    @staticmethod
    def get_cache() -> str:
        return Cache.cache

    @staticmethod
    def set_cache(newCache: str) -> None:
        Cache.cache = newCache
