from os import path
from .views import  shifts_func
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import *
from django.urls import path

from . import views

urlpatterns = [
    path('<int:id>/', views.shifts_func),
    ]
