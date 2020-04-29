from functools import wraps


def cached(cache_if=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            use_cache = kwargs.pop('use_cache', True)

            if wrapper.cached and use_cache:
                return wrapper.cached_result

            value = func(*args, **kwargs)
            should_cache = True

            if cache_if:
                should_cache = value in cache_if
            if should_cache:
                wrapper.cached = True
                wrapper.cached_result = value

            return value

        wrapper.cached = False
        wrapper.cached_result = None
        return wrapper
    return decorator
