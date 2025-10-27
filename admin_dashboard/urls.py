from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('kelola-user/', views.kelola_user_view, name='kelola_user'),
    path('tambah-user/', views.tambah_user_view, name='tambah_user'),
    path('edit-user/<int:id>/', views.edit_user_view, name='edit_user'),

    path('data-hama/', views.data_hama_view, name='data_hama'),
    path('tambah-hama/', views.tambah_hama_view, name='tambah_hama'),       # <-- tambah ini
    path('edit-hama/<int:id>/', views.edit_hama_view, name='edit_hama'),    # <-- dan ini (opsional)
    path('data-pencegahan/', views.data_pencegahan_view, name='data_pencegahan'),
    path('tambah-pencegahan/', views.tambah_pencegahan_view, name='tambah_pencegahan'),  # ⬅️ tambahkan ini

    path('data-lahan/', views.data_lahan_view, name='data_lahan'),
    path('tambah-lahan/', views.tambah_lahan_view, name='tambah_lahan'),
    path('edit-lahan/<int:id>/', views.edit_lahan_view, name='edit_lahan'),
]
