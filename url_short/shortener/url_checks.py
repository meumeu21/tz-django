import ipaddress
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.core.exceptions import ValidationError


def normalize_url(url):
    parts = urlsplit(url)
    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip('/') or '/',
        parts.query,
        parts.fragment,
    ))


def check_url(url):
    parts = urlsplit(url)
    hostname = parts.hostname or ''

    if parts.username or parts.password:
        raise ValidationError('Ссылки с логином или паролем в адресе запрещены')

    for host in settings.ALLOWED_HOSTS:
        host = host.lower().lstrip('.')
        if hostname == host or hostname.endswith('.' + host):
            raise ValidationError('Нельзя сокращать ссылки на сам сервис')

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return
    if not ip.is_global:
        raise ValidationError('Ссылка ведет на внутренний или локальный адрес')
