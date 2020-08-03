from django.conf.urls import url
from django.urls import path
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('query/', views.index),
    path('query/<str:sources>/<str:search_terms>/', views.results),
    path('files/<str:filename>/', views.show_file)
]
