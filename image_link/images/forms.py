from django import forms
from django.template.defaultfilters import filesizeformat

from .image_checks import ALLOWED_FORMATS, MAX_IMAGE_SIZE
from .models import Image, file_sha256


ACCEPTED_TYPES = ','.join(f'image/{image_format.lower()}' for image_format in ALLOWED_FORMATS)


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['file']
        labels = {
            'file': 'Картинка, которую надо загрузить',
        }
        help_texts = {
            'file': f'{", ".join(ALLOWED_FORMATS)}, не больше {filesizeformat(MAX_IMAGE_SIZE)}',
        }
        widgets = {
            'file': forms.FileInput(attrs={'accept': ACCEPTED_TYPES}),
        }

    def save(self, commit=True):
        uploaded = self.cleaned_data['file']
        sha256 = file_sha256(uploaded)
        image = Image.objects.filter(sha256=sha256).first()
        if image is not None:
            return image
        self.instance.sha256 = sha256
        self.instance.original_name = uploaded.name
        return super().save(commit)
