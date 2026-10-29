from django import template

register = template.Library()


def short_url(context, link):
    return context['request'].build_absolute_uri(link.get_absolute_url())


register.simple_tag(short_url, takes_context=True)
