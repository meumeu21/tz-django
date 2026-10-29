from django import forms

from .models import Link
from .url_checks import normalize_url


SORT_COLUMNS = [
    ('original_link', 'Исходная ссылка'),
    ('created_at', 'Создана'),
]
DEFAULT_SORT = '-created_at'
SEARCH_QUERY_MAX_LENGTH = 200


def https_formfield(field, **kwargs):
    return field.formfield(assume_scheme='https', **kwargs)


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
        formfield_callback = https_formfield

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

    def get_query(self):
        return self.cleaned_data.get('q', '')

    def get_sort(self):
        return self.cleaned_data.get('sort') or DEFAULT_SORT

    def sort_columns(self):
        current_sort = self.get_sort()
        columns = []
        for field, label in SORT_COLUMNS:
            if current_sort == field:
                direction, next_sort = 'asc', '-' + field
            elif current_sort == '-' + field:
                direction, next_sort = 'desc', field
            else:
                direction, next_sort = None, field
            columns.append({'label': label, 'direction': direction, 'next_sort': next_sort})
        return columns
