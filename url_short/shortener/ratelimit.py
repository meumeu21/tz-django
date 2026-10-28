from django.core.cache import cache

MINUTE = 60
DAY = 24 * 60 * MINUTE
REQUESTS_PER_MINUTE = 10
REQUESTS_PER_DAY = 100
LIMITS = [(REQUESTS_PER_MINUTE, MINUTE), (REQUESTS_PER_DAY, DAY)]
CACHE_KEY_PREFIX = 'ratelimit:create'


def is_rate_limited(request):
    ip = request.META.get('REMOTE_ADDR')
    limited = False
    for limit, period in LIMITS:
        key = f'{CACHE_KEY_PREFIX}:{ip}:{period}'
        cache.add(key, 0, period)
        if cache.incr(key) > limit:
            limited = True
    return limited
