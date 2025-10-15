from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Dashboard (namespace opsional)
    path('', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),

    # Accounts
    path('accounts/', include('accounts.urls')),

    # Detection & Recommendation
    path('detection/', include('detection.urls')),
    path('recommendation/', include('recommendation.urls')),
]
