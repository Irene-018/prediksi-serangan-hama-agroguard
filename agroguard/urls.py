# agroguard/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views   # kalau views kamu pindahkan ke dashboard

urlpatterns = [
    # Root URL will point to the dashboard home
    path('', include('dashboard.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('admin_dashboard/', include('admin_dashboard.urls')),
    path("rekomendasi/<int:detection_id>/", views.recommendation_detail, name="rekomendasi_detail"),
]


# Serve media files saat development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)