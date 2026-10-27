import secrets
import string

from django.core.validators import URLValidator
from django.db import models, IntegrityError, transaction
from django.urls import reverse


ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
MAX_CODE_LENGTH = 10
MAX_LINK_LENGTH = 2048
ATTEMPTS_GENERATE_CODE = 10


def generate_short_code(length=CODE_LENGTH):
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))


class Link(models.Model):
    original_link = models.URLField(
        'исходная ссылка',
        max_length=MAX_LINK_LENGTH,
        validators=[URLValidator(schemes=['http', 'https'])],
    )
    short_code = models.CharField('код', max_length=MAX_CODE_LENGTH, unique=True, editable=False)
    created_at = models.DateTimeField('создана', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ссылка'
        verbose_name_plural = 'ссылки'

    def __str__(self):
        return self.original_link

    def get_absolute_url(self):
        return reverse('shortener:follow', args=[self.short_code])

    def save(self, *args, **kwargs):
        if self.short_code:
            return super().save(*args, **kwargs)
        for _ in range(ATTEMPTS_GENERATE_CODE):
            self.short_code = generate_short_code()
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                continue
        raise RuntimeError('Не удалось сгенерировать уникальный код')
