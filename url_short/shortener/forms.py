from django import forms

from .models import Link
from .url_checks import check_url, normalize_url


SORT_COLUMNS = [
    ('short_code', 'Короткая ссылка'),
    ('original_link', 'Исходная ссылка'),
    ('created_at', 'Создана'),
]
DEFAULT_SORT = '-created_at'


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


class LinkSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'type': 'search',
            'class': 'form-control',
            'placeholder': 'Поиск по ссылке или коду',
            'aria-label': 'Поиск',
        }),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[(prefix + field, '') for field, _ in SORT_COLUMNS for prefix in ('', '-')],
        widget=forms.HiddenInput,
    )
