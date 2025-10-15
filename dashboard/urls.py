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

    # ======================
    # ADMIN DASHBOARD
    # ======================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ======================
    # CRUD PENCEGAHAN HAMA
    # ======================
    path('pencegahan/', views.pencegahan_list, name='pencegahan_list'),
    path('pencegahan/tambah/', views.tambah_pencegahan, name='tambah_pencegahan'),
    path('pencegahan/<int:id>/edit/', views.edit_pencegahan, name='edit_pencegahan'),
    path('pencegahan/<int:id>/hapus/', views.hapus_pencegahan, name='hapus_pencegahan'),
    path('pencegahan/<int:id>/', views.detail_pencegahan, name='detail_pencegahan'),

    # ======================
    # LOGIN & LOGOUT
    # ======================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
