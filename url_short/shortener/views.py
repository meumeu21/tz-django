from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseRedirect

from http import HTTPStatus

from .forms import LinkForm
from .models import Link
from .ratelimit import is_rate_limited


LINKS_PER_PAGE = 20
MY_LINKS_LIMIT = 5
MY_LINKS_SESSION_KEY = 'my_links'


def create_link(request):
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if is_rate_limited(request):
            messages.error(request, 'Слишком много запросов')
            return render_create_page(request, form, HTTPStatus.TOO_MANY_REQUESTS)
        if form.is_valid():
            url = form.cleaned_data['original_link']
            link = Link.objects.filter(original_link=url).first()
            if link is None:
                link = form.save()
            remember_link(request, link)
            messages.success(request, 'Ссылка сокращена')
            return redirect('shortener:create')
    else:
        form = LinkForm()
    return render_create_page(request, form)


def remember_link(request, link):
    codes = request.session.get(MY_LINKS_SESSION_KEY, [])
    if link.short_code in codes:
        codes.remove(link.short_code)
    codes.insert(0, link.short_code)
    request.session[MY_LINKS_SESSION_KEY] = codes[:MY_LINKS_LIMIT]


def get_my_links(request):
    codes = request.session.get(MY_LINKS_SESSION_KEY, [])
    links_by_code = Link.objects.in_bulk(codes, field_name='short_code')
    my_links = [links_by_code[code] for code in codes if code in links_by_code]
    add_short_urls(request, my_links)
    return my_links


def add_short_urls(request, links):
    for link in links:
        link.short_url = request.build_absolute_uri(link.get_absolute_url())


def render_create_page(request, form, status=HTTPStatus.OK):
    context = {'form': form, 'my_links': get_my_links(request)}
    return render(request, 'shortener/create.html', context, status=status)


def follow_link(request, code):
    link = get_object_or_404(Link, short_code=code)
    return HttpResponseRedirect(link.original_link)


def link_list(request):
    paginator = Paginator(Link.objects.all(), LINKS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    add_short_urls(request, page_obj)
    return render(request, 'shortener/link_list.html', {'page_obj': page_obj})
