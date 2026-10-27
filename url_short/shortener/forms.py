from urllib.parse import urlparse

from django import forms
from django.conf import settings

from .models import Link
from .url_checks import check_url, normalize_url


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
        url = normalize_url(self.cleaned_data['original_link'])
        check_url(url)
        return url
