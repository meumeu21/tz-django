from django.urls import path

from . import views

app_name = 'shortener'

urlpatterns = [
    path('', views.create_link, name='create'),
    path('list-links/', views.link_list, name='list'),
    path('<str:code>/', views.follow_link, name='follow'),
]
