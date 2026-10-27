from django.core.cache import cache

LIMITS = [(10, 60), (100, 60 * 60 * 24)]


def is_rate_limited(request):
    ip = request.META.get('REMOTE_ADDR')
    limited = False
    for limit, period in LIMITS:
        key = f'ratelimit:create:{ip}:{period}'
        cache.add(key, 0, period)
        if cache.incr(key) > limit:
            limited = True
    return limited
