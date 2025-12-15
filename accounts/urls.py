# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'  # ✅ Penting! Harus ada ini

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_petani, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),  # 👈 baru
    path('verify-reset-code/', views.verify_reset_code_view, name='verify_reset_code'),  # ✅ Tambahkan ini
    path('reset-password/', views.reset_password_view, name='reset_password'),
]