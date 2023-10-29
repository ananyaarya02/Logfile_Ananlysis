from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('result/', views.upload_file, name="upload_file")
]
