from django.urls import path
from . import views

urlpatterns = [
    path('', views.detect_leaf_page, name='detect_leaf'),
]
