# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'  # ✅ Penting! Harus ada ini

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_petani, name='register'),
    path('logout/', views.logout_view, name='logout'),
]