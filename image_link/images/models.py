import hashlib
import secrets
import string
import uuid

from django.db import models, IntegrityError, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse

from .image_checks import FORMAT_EXTENSIONS, check_image, get_image_format


ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 8
MAX_CODE_LENGTH = 10
ATTEMPTS_GENERATE_CODE = 10
UPLOAD_DIR = 'images'
MAX_ORIGINAL_NAME_LENGTH = 255


def generate_code(length=CODE_LENGTH):
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))


def image_upload_to(instance, filename):
    extension = FORMAT_EXTENSIONS.get(get_image_format(instance.file), '')
    return f'{UPLOAD_DIR}/{uuid.uuid4().hex}{extension}'


def file_sha256(file):
    digest = hashlib.sha256()
    for chunk in file.chunks():
        digest.update(chunk)
    return digest.hexdigest()


class Image(models.Model):
    file = models.ImageField(
        'файл',
        upload_to=image_upload_to,
        width_field='width',
        height_field='height',
        validators=[check_image],
    )
    code = models.CharField('код', max_length=MAX_CODE_LENGTH, unique=True, editable=False)
    original_name = models.CharField('исходное имя', max_length=MAX_ORIGINAL_NAME_LENGTH, blank=True)
    width = models.PositiveIntegerField('ширина', editable=False)
    height = models.PositiveIntegerField('высота', editable=False)
    sha256 = models.CharField('SHA-256', max_length=64, editable=False, db_index=True)
    created_at = models.DateTimeField('загружена', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'картинка'
        verbose_name_plural = 'картинки'

    def __str__(self):
        return self.original_name or self.code

    def get_absolute_url(self):
        return reverse('images:detail', args=[self.code])

    def save(self, *args, **kwargs):
        if not self.sha256:
            self.sha256 = file_sha256(self.file)
        if self.code:
            return super().save(*args, **kwargs)
        for _ in range(ATTEMPTS_GENERATE_CODE):
            self.code = generate_code()
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                if not Image.objects.filter(code=self.code).exists():
                    raise
        raise RuntimeError('Не удалось сгенерировать уникальный код')


@receiver(post_delete, sender=Image)
def delete_image_file(sender, instance, **kwargs):
    transaction.on_commit(lambda: instance.file.delete(save=False))
