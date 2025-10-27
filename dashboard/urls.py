# dashboard/urls.py (Setelah Perbaikan)
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ======================
    # DASHBOARD USER
    # ======================
    path('', views.dashboard_view, name='home'),
    path('deteksi/', views.deteksi_view, name='deteksi'),
    path('rekomendasi/', views.rekomendasi_view, name='rekomendasi'),
    path('riwayat/', views.riwayat_view, name='riwayat'),
    path('pengaturan/', views.pengaturan_view, name='pengaturan'),
    path('profile/', views.profile_view, name='profile'),
    # ======================
    # ADMIN DASHBOARD - TELAH DIHAPUS DARI SINI
    # ======================
    # path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'), # <--- HAPUS BARIS INI
    
    # ... (sisa path)
]