from django.urls import path
from . import views

app_name = 'dashboard'  # ← penting! tambahkan ini

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('deteksi/', views.deteksi_view, name='deteksi'),
    path('rekomendasi/', views.rekomendasi_view, name='rekomendasi'),
    path('riwayat/', views.riwayat_view, name='riwayat'),
]
