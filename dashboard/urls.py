# dashboard/urls.py (Setelah Perbaikan)
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard pages
    path('', views.dashboard_view, name='home'),
    path('deteksi/', views.deteksi_view, name='deteksi'),
    path('rekomendasi/', views.rekomendasi_view, name='rekomendasi'),
    path("rekomendasi/<int:detection_id>/", views.recommendation_detail, name="recommendation_detail"),
    path('recommendation/<int:detection_id>/', views.rekomendasi_view, name='recommendation'),
    path('riwayat/', views.riwayat_view, name='riwayat'),
    path('riwayat/export_pdf/', views.export_pdf, name='export_pdf'),
    path('pengaturan/', views.pengaturan_view, name='pengaturan'),
    path('profile/', views.profile_view, name='profile'),
    
    # API endpoints
    path('api/test/', views.test_api, name='test_api'),
    path('api/sensor/data/', views.receive_sensor_data, name='receive_sensor_data'),
    path('api/sensor/latest/', views.get_latest_sensor_data, name='get_latest_sensor_data'),
    path('api/sensor/statistics/', views.get_statistics, name='get_statistics'),  # ← TAMBAH INI
    path('api/sensor/chart/raw/', views.get_sensor_chart_raw, name='get_sensor_chart_raw'),
    path('api/ai/detect/', views.proses_deteksi_ai, name='ai_detect'),
]