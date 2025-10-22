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
    # LOGIN & LOGOUT
    # ======================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update-password/', views.update_password, name='update_password'),
]