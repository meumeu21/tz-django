from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'shortener'

urlpatterns = [
    path('', views.create_link, name='create'),
    path('list-links', RedirectView.as_view(pattern_name='shortener:list', permanent=True, query_string=True)),
    path('list-links/', views.link_list, name='list'),
    path('<str:code>', views.follow_link, name='follow'),
]
