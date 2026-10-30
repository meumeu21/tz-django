from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from PIL import Image as PILImage


MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
FORMAT_EXTENSIONS = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'GIF': '.gif',
    'WEBP': '.webp',
}
ALLOWED_FORMATS = tuple(FORMAT_EXTENSIONS)
TOO_MANY_PIXELS_MESSAGE = f'Изображение больше {MAX_IMAGE_PIXELS // 1_000_000} мегапикселей'
NOT_AN_IMAGE_MESSAGE = 'Файл не является изображением JPEG, PNG, GIF или WEBP'


def get_image_format(file):
    try:
        file.seek(0)
        with PILImage.open(file, formats=ALLOWED_FORMATS) as image:
            return image.format
    except Exception:
        return None
    finally:
        file.seek(0)


def check_image(file):
    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError(f'Размер файла больше {filesizeformat(MAX_IMAGE_SIZE)}')
    try:
        file.seek(0)
        with PILImage.open(file, formats=ALLOWED_FORMATS) as image:
            pixels = image.width * image.height
            image.verify()
    except PILImage.DecompressionBombError as error:
        raise ValidationError(TOO_MANY_PIXELS_MESSAGE) from error
    except Exception as error:
        raise ValidationError(NOT_AN_IMAGE_MESSAGE) from error
    finally:
        file.seek(0)
    if pixels > MAX_IMAGE_PIXELS:
        raise ValidationError(TOO_MANY_PIXELS_MESSAGE)
