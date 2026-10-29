from http import HTTPStatus

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import LinkForm, DEFAULT_SORT
from .models import Link, CODE_LENGTH
from .ratelimit import REQUESTS_PER_MINUTE
from .url_checks import normalize_url


URL = 'https://example.com/'
CREATE_URL = reverse('shortener:create')
LIST_URL = reverse('shortener:list')


class NormalizeUrlTests(TestCase):
    def test_lowercases_scheme_and_host_only(self):
        self.assertEqual(normalize_url('HTTPS://Example.COM/Path'), 'https://example.com/Path')

    def test_trailing_slash_is_ignored(self):
        self.assertEqual(normalize_url('https://example.com/page/'), 'https://example.com/page')
        self.assertEqual(normalize_url('https://example.com/page//'), 'https://example.com/page')

    def test_root_path(self):
        self.assertEqual(normalize_url('https://example.com'), 'https://example.com/')
        self.assertEqual(normalize_url('https://example.com/'), 'https://example.com/')

    def test_keeps_query_and_fragment(self):
        self.assertEqual(normalize_url('https://example.com/a/?x=1#top'), 'https://example.com/a?x=1#top')


@override_settings(ALLOWED_HOSTS=['testserver'])
class LinkFormTests(TestCase):
    def assert_invalid(self, url):
        self.assertFalse(LinkForm({'original_link': url}).is_valid(), url)

    def test_valid_url(self):
        form = LinkForm({'original_link': f'{URL}a/'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['original_link'], f'{URL}a')

    def test_scheme_is_https_by_default(self):
        form = LinkForm({'original_link': 'example.com'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['original_link'], URL)

    def test_rejects_forbidden_urls(self):
        self.assert_invalid('ftp://example.com/')
        self.assert_invalid('https://user:pass@example.com/')
        self.assert_invalid('http://testserver/abc')
        self.assert_invalid('http://127.0.0.1/')
        self.assert_invalid('http://192.168.0.1/')


@override_settings(ALLOWED_HOSTS=['testserver'])
class CreateLinkTests(TestCase):
    def setUp(self):
        cache.clear()

    def shorten(self, url=URL):
        return self.client.post(CREATE_URL, {'original_link': url})

    def test_create_link(self):
        self.assertRedirects(self.shorten(), CREATE_URL)
        self.assertEqual(len(Link.objects.get().short_code), CODE_LENGTH)

    def test_same_link_is_not_duplicated(self):
        self.shorten(f'{URL}page')
        self.shorten('https://EXAMPLE.com/page/')
        self.assertEqual(Link.objects.count(), 1)

    def test_create_page_shows_latest_link(self):
        self.shorten()
        response = self.client.get(CREATE_URL)
        self.assertEqual(response.context['latest_link'], Link.objects.get())

    def test_rate_limit(self):
        for i in range(REQUESTS_PER_MINUTE):
            self.shorten(f'{URL}{i}')
        response = self.shorten(f'{URL}extra')
        self.assertEqual(response.status_code, HTTPStatus.TOO_MANY_REQUESTS)
        self.assertEqual(Link.objects.count(), REQUESTS_PER_MINUTE)


class FollowLinkTests(TestCase):
    def test_follow_link(self):
        link = Link.objects.create(original_link=URL)
        response = self.client.get(link.get_absolute_url())
        self.assertRedirects(response, URL, fetch_redirect_response=False)

    def test_follow_unknown_code(self):
        response = self.client.get(reverse('shortener:follow', args=['nope42']))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class LinkListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.python = Link.objects.create(original_link='https://python.org/')
        cls.django = Link.objects.create(original_link='https://djangoproject.com/')

    def search(self, query):
        return list(self.client.get(LIST_URL, {'q': query}).context['page_obj'])

    def test_search_by_original_link(self):
        self.assertEqual(self.search('python'), [self.python])

    def test_search_by_short_url(self):
        self.assertEqual(self.search(f'http://testserver/{self.python.short_code}'), [self.python])

    def test_invalid_sort_falls_back_to_default(self):
        response = self.client.get(LIST_URL, {'sort': 'short_code'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['sort'], DEFAULT_SORT)
