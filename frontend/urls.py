from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('deteksi/', views.deteksi, name='deteksi'),
    path('rekomendasi/', views.rekomendasi, name='rekomendasi'),
    path('riwayat/', views.riwayat, name='riwayat'),
    path('profile/', views.profile, name='profile'),
]
