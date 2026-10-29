from django import forms

from .models import Link
from .url_checks import normalize_url


SORT_COLUMNS = [
    ('original_link', 'Исходная ссылка'),
    ('created_at', 'Создана'),
]
DEFAULT_SORT = '-created_at'
SEARCH_QUERY_MAX_LENGTH = 200


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
        return normalize_url(self.cleaned_data['original_link'])


class LinkSearchForm(forms.Form):
    q = forms.CharField(
        label='Поиск',
        required=False,
        max_length=SEARCH_QUERY_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'type': 'search',
            'placeholder': 'Поиск по ссылке или коду',
        }),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[(prefix + field, '') for field, _ in SORT_COLUMNS for prefix in ('', '-')],
        widget=forms.HiddenInput,
    )
