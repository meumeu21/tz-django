from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.core.cache import cache

from http import HTTPStatus

from .forms import LinkForm
from .models import Link


LINKS_PER_PAGE = 20
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


def create_link(request):
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if is_rate_limited(request):
            messages.error(request, 'Слишком много запросов')
            return render(request, 'shortener/create.html', {'form': form}, status=HTTPStatus.TOO_MANY_REQUESTS)
        if form.is_valid():
            url = form.cleaned_data['original_link']
            link = Link.objects.filter(original_link=url).first()
            if link is None:
                link = form.save()
            
            short_url = request.build_absolute_uri(
                reverse('shortener:follow', args=[link.short_code])
            )
            messages.success(request, f'Готово: {short_url}')
            return redirect('shortener:create')
    else:
        form = LinkForm()
    return render(request, 'shortener/create.html', {'form': form})


def follow_link(request, code):
    link = get_object_or_404(Link, short_code=code)
    return redirect(link.original_link)


def link_list(request):
    paginator = Paginator(Link.objects.all(), LINKS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'shortener/link_list.html', {'page_obj': page_obj})
