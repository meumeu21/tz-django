from urllib.parse import urlparse

from django import forms
from django.conf import settings

from .models import Link


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['original_link']
        labels = {
            'original_link': 'Ссылка, которую надо сократить',
        }
        widgets = {
            'original_link': forms.URLInput(attrs={'placeholder': 'https://URL-вашей-ссылки.com/...'}),
        }

    def clean_original_link(self):
        url = self.cleaned_data['original_link']
        hostname = (urlparse(url).hostname or '').lower()
        for host in settings.ALLOWED_HOSTS:
            host = host.lower().lstrip('.')
            if hostname == host or hostname.endswith('.' + host):
                raise forms.ValidationError('Нельзя сокращать ссылки на сам сервис')
        return url
