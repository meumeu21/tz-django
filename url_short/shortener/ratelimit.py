import ipaddress

from django.conf import settings
from django.core.cache import cache

MINUTE = 60
DAY = 24 * 60 * MINUTE
REQUESTS_PER_MINUTE = 10
REQUESTS_PER_DAY = 100
LIMITS = [(REQUESTS_PER_MINUTE, MINUTE), (REQUESTS_PER_DAY, DAY)]
CACHE_KEY_PREFIX = 'ratelimit:create'
IPV6_PREFIX_LENGTH = 64


def get_client_ip(request):
    if settings.BEHIND_PROXY:
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            return forwarded.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR')


def get_rate_limit_key(ip):
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return 'unknown'
    if address.version == 6:
        network = ipaddress.ip_network(f'{address}/{IPV6_PREFIX_LENGTH}', strict=False)
        return str(network.network_address)
    return ip


def is_rate_limited(request):
    client = get_rate_limit_key(get_client_ip(request))
    for limit, period in LIMITS:
        key = f'{CACHE_KEY_PREFIX}:{client}:{period}'
        cache.add(key, 0, period)
        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, period)
            count = 1
        if count > limit:
            return True
    return False
