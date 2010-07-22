# memoize.py
# From http://programmingzen.com/2009/05/18/memoization-in-ruby-and-python/

def memoize(function):
    cache = {}
    def decorated_function(*args):
        if args in cache:
            return cache[args]
        else:
            val = function(*args)
            cache[args] = val
            return val
    return decorated_function