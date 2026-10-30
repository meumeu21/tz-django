from django import template

register = template.Library()


def absolute_url(context, path):
    return context['request'].build_absolute_uri(path)


register.simple_tag(absolute_url, takes_context=True)
