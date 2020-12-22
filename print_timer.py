from timeit import default_timer as timer

count = 0

def print_timer(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kw):
        global count
        count += 1
        start = timer()
        result = func(*args, **kw)
        end = timer()
        spacer = ' ' * count if count > 1 else ''
        print("%s%r: %f ms" % (spacer, func.__name__, (end - start) * 1000))
        count -= 1
        return result
    return wrapper
