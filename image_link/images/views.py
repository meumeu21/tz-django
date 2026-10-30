from http import HTTPStatus

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ImageForm
from .models import Image
from .ratelimit import is_rate_limited


PREVIOUS_IMAGES_LIMIT = 5
MY_IMAGES_SESSION_KEY = 'my_images'


def upload_image(request):
    if request.method == 'POST':
        if is_rate_limited(request):
            messages.error(request, 'Слишком много запросов')
            return render_upload_page(request, ImageForm(), HTTPStatus.TOO_MANY_REQUESTS)
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            remember_image(request, image)
            messages.success(request, 'Картинка загружена')
            return redirect('images:upload')
    else:
        form = ImageForm()
    return render_upload_page(request, form)


def remember_image(request, image):
    codes = request.session.get(MY_IMAGES_SESSION_KEY, [])
    if image.code in codes:
        codes.remove(image.code)
    codes.insert(0, image.code)
    request.session[MY_IMAGES_SESSION_KEY] = codes[:PREVIOUS_IMAGES_LIMIT + 1]


def get_my_images(request):
    codes = request.session.get(MY_IMAGES_SESSION_KEY, [])
    images_by_code = Image.objects.in_bulk(codes, field_name='code')
    return [images_by_code[code] for code in codes if code in images_by_code]


def render_upload_page(request, form, status=HTTPStatus.OK):
    my_images = get_my_images(request)
    context = {
        'form': form,
        'latest_image': my_images[0] if my_images else None,
        'previous_images': my_images[1:],
    }
    return render(request, 'images/upload.html', context, status=status)
